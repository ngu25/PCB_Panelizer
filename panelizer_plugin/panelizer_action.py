import pcbnew
import os
import wx
from .panelizer_gui import PanelizerDialog
from .utils import get_board_bbox, get_board_size_mm, add_rect_edge_cuts, extract_poly, render_poly


class PanelizerAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Panelizer"
        self.category = "Panelize"
        self.description = "Panelize PCB with V-Score and Mousebites"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
        self.dark_icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")

    def GetIconFileName(self, dark=False):
        return os.path.join(os.path.dirname(__file__), "icon.png")

    def Run(self):
        board = pcbnew.GetBoard()
        dialog = PanelizerDialog()

        if dialog.ShowModal() == wx.ID_OK:
            settings = dialog.GetSettings()
            if settings:
                self.panelize(board, settings)

        dialog.Destroy()

    # ------------------------------------------------------------------
    # Step 1 Redo: Geometric Expansion & Fusing
    # ------------------------------------------------------------------
    def panelize(self, board, settings):
        # 1. Basic Dimensions
        bbox = get_board_bbox(board)
        if not bbox:
            wx.MessageBox("No Edge.Cuts found!", "Error")
            return
            
        board_w = bbox.GetWidth()
        board_h = bbox.GetHeight()
        board_x = bbox.GetX()
        board_y = bbox.GetY()
        
        # 2. Settings
        cols = settings["cols"]
        rows = settings["rows"]
        gap_mm = settings["gap_mm"]
        method = settings.get("method", "V-Cut")
        gap = pcbnew.FromMM(gap_mm)
        
        panel_w = pcbnew.FromMM(settings["panel_w_mm"])
        panel_h = pcbnew.FromMM(settings["panel_h_mm"])
        
        # 3. Create Array
        original_items = []
        original_items.extend(board.Tracks())
        original_items.extend(board.Footprints())
        # Filter Drawings based on Method
        for d in board.Drawings():
            if method == "V-Cut" and d.GetLayer() == pcbnew.Edge_Cuts:
                continue
            original_items.append(d)
        original_items.extend(board.Zones())
        
        # Calculate array total size
        array_w = cols * board_w + (cols - 1) * gap
        array_h = rows * board_h + (rows - 1) * gap

        # Validation: Check if Panel Size is sufficient
        # Use a small tolerance for float comparison or just strict check
        if panel_w < array_w or panel_h < array_h:
            msg = "Error: Panel size is too small!\n\n" \
                  "Required: {:.2f} mm x {:.2f} mm\n" \
                  "Specified: {:.2f} mm x {:.2f} mm".format(
                      pcbnew.ToMM(array_w), pcbnew.ToMM(array_h),
                      pcbnew.ToMM(panel_w), pcbnew.ToMM(panel_h)
                  )
            wx.MessageBox(msg, "Panel Too Small", wx.OK | wx.ICON_ERROR)
            return

        # Calculate Frame Position (Centered)
        margin_x = (panel_w - array_w) / 2
        margin_y = (panel_h - array_h) / 2
        frame_x = board_x - margin_x
        frame_y = board_y - margin_y
        
        # Replicate Items
        # Move original items if needed? No, original items are at (0,0) relative to board.
        # Wait, if we are panelizing, users usually expect the original board to be part of the panel.
        # But `board.Add(dup)` adds to the existing board.
        # The existing board items are ALREADY there.
        # Problem: If we filter Edge.Cuts, we need to REMOVE the original Edge.Cuts too?
        # Yes.
        
        if method == "V-Cut":
             # Remove existing Edge.Cuts from the board (the source)
             # Collect them first to avoid iterator invalidation
             to_remove = []
             for d in board.Drawings():
                 if d.GetLayer() == pcbnew.Edge_Cuts:
                     to_remove.append(d)
             for d in to_remove:
                 board.Remove(d)
        
        # Now replicate.
        # Since we removed original Edge.Cuts, `original_items` logic needs care.
        # If we already captured them in `original_items` before removal?
        # Capturing `board.Drawings()` creates wrappers.
        # If we remove them from board, the wrappers might be stale or invalid if not careful (though typically in Python scripting it's by ref).
        # Better strategy: Capture everything into list of CLONES first?
        # Or:
        # The Loop:
        # For r, c:
        #   if r==0, c==0: 
        #       Leave original items? 
        #       BUT we just removed Edge.Cuts. 
        #       So original board effectively loses its outline. Correct.
        #   else:
        #       Duplicate `original_items`.
        #       But we verified `original_items` didn't include Edge.Cuts (if we filtered).
        #       Wait, my previous `original_items` logic included them unless filtered.
        
        # Refined Logic:
        # 1. Capture `source_items` (excluding Edge.Cuts if V-Cut).
        # 2. Clear Edge.Cuts from board if V-Cut.
        # 3. Use `source_items` to populate (r,c) > (0,0).
        # 4. (r=0, c=0) is ALREADY populated by the board's existing items.
        #    BUT if we wanted to remove Edge.Cuts from (0,0), we did that in step 2.
        #    AND we must ensure `source_items` does NOT contain the now-removed Edge.Cuts (wrappers might crash?).
        #    So, capture `source_items` (filtering Edge.Cuts) -> Remove Edge.Cuts from board -> Loop.
        
        # Correct.
        
        source_items = []
        source_items.extend(board.Tracks())
        source_items.extend(board.Footprints())
        source_items.extend(board.Zones())
        for d in board.Drawings():
             # If V-Cut, skip Edge.Cuts
             if method == "V-Cut" and d.GetLayer() == pcbnew.Edge_Cuts:
                 continue
             source_items.append(d)

        # If V-Cut, remove existing Edge.Cuts from the board now
        if method == "V-Cut":
            to_remove = [d for d in board.Drawings() if d.GetLayer() == pcbnew.Edge_Cuts]
            for d in to_remove:
                board.Remove(d)

        for r in range(rows):
            for c in range(cols):
                if r == 0 and c == 0:
                    continue # Original board items are already there (minus Edge.Cuts if removed)
                    
                dx = c * (board_w + gap)
                dy = r * (board_h + gap)
                vec = pcbnew.VECTOR2I(int(dx), int(dy))
                
                for item in source_items:
                    dup = item.Duplicate()
                    dup.Move(vec)
                    board.Add(dup)

        # 4. Render Panel Frame
        # User requested frame width = gap
        add_rect_edge_cuts(board, frame_x, frame_y, panel_w, panel_h, width=gap)

        # 5. V-Cuts
        # 5. V-Cuts
        if method == "V-Cut":
            # Calculate all Cut Positions first
            # Vertical Cuts (X positions)
            cut_x_positions = []
            for c in range(cols + 1):
                cut_x = board_x + c * (board_w + gap) - (gap // 2)
                cut_x_positions.append(cut_x)
            
            # Horizontal Cuts (Y positions)
            cut_y_positions = []
            for r in range(rows + 1):
                cut_y = board_y + r * (board_h + gap) - (gap // 2)
                cut_y_positions.append(cut_y)
                
            # Limits for lines
            # Vertical lines go from: frame_y to frame_y + panel_h
            # Actually, if we want them to intersect, they form a grid.
            # Vertical lines should be drawn from:
            #   Start: frame_y
            #   End: frame_y + panel_h
            # BUT user asked to "end the line at the intersection point".
            # This implies if we have a grid, we draw segments between intersection points.
            
            # Intersection points are (x, y) where x in cut_x_positions, y in cut_y_positions.
            # Plus the frame boundaries?
            # The V-Cuts extend to the Panel Frame.
            # The Cut Positions calculated above encompass the panel logic?
            # cut_x[0] is Left Edge (roughly frame_x?). 
            #   frame_x = board_x - margin_x. 
            #   cut_x[0] = board_x - gap/2.
            #   If gap/2 != margin, they differ.
            #   Usually margin >= gap/2.
            # Let's assume the lines extend FULLY from Top Frame to Bottom Frame.
            # But the user wants them "intersecting... end at intersection".
            # This means we draw segments:
            # For a vertical line at X:
            #   Segments are from Y_start to Y_intersection_1, Y_int_1 to Y_int_2...
            #   The intersections are the Horizontal Cuts.
            #   So we iterate Y positions.
            
            # We also need the Frame Top/Bottom boundaries as "intersections" or start/end points?
            # Yes. 
            # Let's collect all Y boundaries: Frame_Top, Cut_Y_0, Cut_Y_1 ... Cut_Y_N, Frame_Bottom.
            # Wait, `cut_y_positions` might be inside or outside frame depending on logic.
            # `cut_y` formula: board_y + r*(h+g) - g/2.
            # Frame Top: board_y - margin_y.
            # Should we clamp them?
            # Let's use the explicit Cut coordinates.
            
            # Vertical Segments
            # For each X cut:
            #   Iterate through all Y cuts (plus panel bounds?)
            #   Actually, the "grid" is formed by the cuts themselves.
            #   Do we include the Frame Edges as "Intersections"?
            #   If we don't, the lines floating inside the frame won't touch the frame.
            #   User said "Draw it until the edge of the main panel".
            #   So the line goes from Frame Top to Frame Bottom.
            #   And it intersects every Horizontal Cut.
            #   So we split it at every Horizontal Cut.
            
            # Y Points for splitting Vertical lines:
            # [Frame_Top] + cut_y_positions + [Frame_Bottom] ?
            # cut_y[0] is usually close to Frame Top.
            # cut_y[rows] is close to Frame Bottom.
            # Let's simplify: split at every `cut_y`.
            # AND clamp to Frame.
            
            y_points = sorted([frame_y] + cut_y_positions + [frame_y + panel_h])
            # Remove duplicates/cleanup?
            # Filter points within panel range?
            y_points = [y for y in y_points if y >= frame_y and y <= frame_y + panel_h]
            y_points = sorted(list(set(y_points)))

            # Horizontal Points: ONLY the cut positions (trim outer bits)
            x_points = sorted(cut_x_positions)
            # x_points = [x for x in x_points if x >= frame_x and x <= frame_x + panel_w] # Implicitly true
            x_points = sorted(list(set(x_points)))
            
            # Fix for KiCad 9 Angle
            try:
                angle_90 = pcbnew.EDA_ANGLE(90.0, pcbnew.DEGREES_T)
                angle_0 = pcbnew.EDA_ANGLE(0.0, pcbnew.DEGREES_T)
            except AttributeError:
                try:
                    angle_90 = pcbnew.EDA_ANGLE(90.0, pcbnew.DEGREES)
                    angle_0 = pcbnew.EDA_ANGLE(0.0, pcbnew.DEGREES)
                except:
                    angle_90 = pcbnew.EDA_ANGLE(900)
                    angle_0 = pcbnew.EDA_ANGLE(0)

            # Draw Vertical Segments
            for x in cut_x_positions:
                for i in range(len(y_points) - 1):
                    y1 = y_points[i]
                    y2 = y_points[i+1]
                    if abs(y2 - y1) < 100: continue # Skip minimal segments
                    
                    seg = pcbnew.PCB_SHAPE(board)
                    seg.SetShape(pcbnew.S_SEGMENT)
                    seg.SetStart(pcbnew.VECTOR2I(int(x), int(y1)))
                    seg.SetEnd(pcbnew.VECTOR2I(int(x), int(y2)))
                    seg.SetLayer(pcbnew.F_Fab) # User requested F.Fab
                    seg.SetWidth(int(gap))   # Thickness = Gap
                    board.Add(seg)
                
                # Add Text (Once per column, OUTSIDE top)
                txt = pcbnew.PCB_TEXT(board)
                txt.SetText("VSCORE")
                txt.SetLayer(pcbnew.F_Fab)
                txt.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
                txt.SetTextThickness(pcbnew.FromMM(0.25))
                txt.SetTextAngle(angle_90) 
                # Position: Center X on line, Y above frame.
                # To clear the frame, move up by e.g. 5mm
                txt.SetPosition(pcbnew.VECTOR2I(int(x), int(frame_y - pcbnew.FromMM(5))))
                board.Add(txt)

            # Draw Horizontal Segments
            for y in cut_y_positions:
                for i in range(len(x_points) - 1):
                    x1 = x_points[i]
                    x2 = x_points[i+1]
                    if abs(x2 - x1) < 100: continue
                    
                    seg = pcbnew.PCB_SHAPE(board)
                    seg.SetShape(pcbnew.S_SEGMENT)
                    seg.SetStart(pcbnew.VECTOR2I(int(x1), int(y)))
                    seg.SetEnd(pcbnew.VECTOR2I(int(x2), int(y)))
                    seg.SetLayer(pcbnew.F_Fab) # User requested F.Fab
                    seg.SetWidth(int(gap))   # Thickness = Gap
                    board.Add(seg)
                    
                # Add Text (Once per row, OUTSIDE left)
                txt = pcbnew.PCB_TEXT(board)
                txt.SetText("VSCORE")
                txt.SetLayer(pcbnew.F_Fab)
                txt.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
                txt.SetTextThickness(pcbnew.FromMM(0.25))
                txt.SetTextAngle(angle_0)
                # Position: Center Y on line, X left of frame
                # To clear the frame, move left by e.g. 5mm
                txt.SetPosition(pcbnew.VECTOR2I(int(frame_x - pcbnew.FromMM(5)), int(y)))
                board.Add(txt)

        elif method == "Mousebites":
            # TODO: Implement Mousebites
            pass
        
        pcbnew.Refresh()
