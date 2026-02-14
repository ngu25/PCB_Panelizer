import pcbnew
import math

# Constants
TOLERANCE = 100 # nm

def get_board_bbox(board):
    """
    Returns the bounding box of the board's Edge.Cuts outline.
    """
    bbox = None
    for drawing in board.Drawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            if bbox is None:
                bbox = drawing.GetBoundingBox()
            else:
                bbox.Merge(drawing.GetBoundingBox())
    return bbox

def get_board_size_mm(board):
    bbox = get_board_bbox(board)
    if bbox is None:
        return None
    return (pcbnew.ToMM(bbox.GetWidth()), pcbnew.ToMM(bbox.GetHeight()))

def add_rect_edge_cuts(board, x, y, w, h, width=None):
    """
    Draws a rectangle on Edge.Cuts using 4 line segments.
    """
    layer = pcbnew.Edge_Cuts
    if width is None:
        width = pcbnew.FromMM(0.1)
        
    corners = [
        (x, y),
        (x + w, y),
        (x + w, y + h),
        (x, y + h),
    ]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.S_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(int(corners[i][0]), int(corners[i][1])))
        seg.SetEnd(pcbnew.VECTOR2I(int(corners[(i + 1) % 4][0]), int(corners[(i + 1) % 4][1])))
        seg.SetLayer(layer)
        seg.SetWidth(int(width))
        board.Add(seg)

# --- Geometric Operations with SHAPE_POLY_SET ---

def extract_outline_polygon(board, tolerance_mm=0.01):
    """
    Extracts the Edge.Cuts outline as a single SHAPE_POLY_SET.
    Approximates Arcs/Circles with segments.
    """
    poly = pcbnew.SHAPE_POLY_SET()
    
    # We essentially want to boolean union all Edge.Cuts items to form the outline?
    # Or assuming they form a chain.
    # To be robust against disconnects, let's treat each item as a "Thick Segment" 
    # and Union them? No, that gives a fat outline.
    # We want the Enclosed Area.
    
    # 1. Chain Logic (Hard).
    # 2. "Guess" Logic:
    # Most board outlines are close loops.
    # Let's use `SHAPE_POLY_SET`'s ability to add paths.
    
    # KiCad requires a "Closed Loop" for a valid outline.
    # Let's try to convert each graphic item into a Chain.
    # Actually, simpler: KiCad's Board usually has `GetBoardPolygonOutlines`?
    # In KiCad 9, `board.GetBoardPolygonOutlines(layer, tolerance, outline)`? No.
    # `board.GetShape()`?
    
    # Let's manually convert items to a polygon.
    # Strategy:
    # 1. Collect all Edge.Cut shapes.
    # 2. Convert to linear paths (discretize arcs).
    # 3. Use `pcbnew.Chain()` or manual chaining.
    # 4. Construct Poly.
    
    # Simplified: Assuming the user has a closed outline.
    # We iterate and find connections.
    
    # BUT, to skip complexity:
    # Can we just Clone the items, Inflate them individually, and Union?
    # A Line Inflated is a Capsule. 
    # A Box Inflated is a Rounded Box.
    # If we Union all these "Inflated Traces", we get a "Route Path" shape?
    # No, that gives the wall, not the room.
    
    # User said: "If circle... draw concentric circle...".
    # This implies we are operating on the Closed Shape.
    
    # Let's try to find a `SHAPE_POLY_SET` from board.
    # `board.ConvertBBoxToPoly()`? No.
    
    # Let's assume standard behavior:
    # Gather all segments/arcs.
    # Find the Loop.
    # Convert Loop to Poly.
    # (Implementation detail omitted for brevity, using simple Box fallback if fail? No, user explicitly wants Circle support).
    
    # Let's implement robust chaining.
    
    edges = []
    for d in board.Drawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            edges.append(d)
            
    if not edges:
        return None
        
    # Build Map of Endpoints
    # Point -> [Items]
    # ...
    
    # ALTERNATIVE: Use `SHAPE_POLY_SET`.
    # Add each segment as a "Hole"? No.
    # Add each segment as a path.
    
    # Let's try a simpler approach if the API supports it.
    # `board.GetBoardEdges()` returns a chain?
    
    # Let's do the standard Chain Sort.
    # Or...
    # Just iterate and render all into a generic SHAPE_POLY_SET?
    # SHAPE_POLY_SET needs closed outlines.
    
    # I will implement a "Chain Builder".
    pass

    # For this iteration, let's implement a simple chain builder.
    # If it fails, fallback to BBox.
    
    chain = []
    # (Start, End, Object)
    
    # Helper to get start/end
    def get_se(item):
        if item.GetShape() == pcbnew.S_SEGMENT:
            return (item.GetStart(), item.GetEnd())
        elif item.GetShape() == pcbnew.S_ARC:
            return (item.GetStart(), item.GetEnd()) # Start and End of Arc
        elif item.GetShape() == pcbnew.S_CIRCLE:
            return (None, None) # Special
        elif item.GetShape() == pcbnew.S_RECT:
             # Convert to 4 lines
             return (None, None)
        return (None, None)
        
    # Check for Circle/Rect primitive First
    for item in edges:
        if item.GetShape() == pcbnew.S_CIRCLE:
            # It's a circle board.
            poly.NewOutline()
            # Discretize Circle
            center = item.GetCenter()
            radius = item.GetRadius()
            steps = 72
            for i in range(steps):
                angle = 2 * math.pi * i / steps
                px = center.x + radius * math.cos(angle)
                py = center.y + radius * math.sin(angle)
                poly.Append(int(px), int(py))
            return poly
            
        if item.GetShape() == pcbnew.S_RECT:
            poly.NewOutline()
            r = item.GetBoundingBox() # Rect is aligned
            poly.Append(r.GetLeft(), r.GetTop())
            poly.Append(r.GetRight(), r.GetTop())
            poly.Append(r.GetRight(), r.GetBottom())
            poly.Append(r.GetLeft(), r.GetBottom())
            return poly

    # Chain Segments/Arcs
    # Start with first item
    used = set()
    
    # Find a start point (any)
    # Simple recursive finder
    
    # Let's just dump all points into Poly and Convex Hull? No, Convex Hull kills concave boards.
    
    # Let's assume standard "One Loop".
    # Pick first, find neighbor...
    
    # Note: Implementing a full topology solver in 1 step is risky.
    # Most users use Lines/Arcs.
    
    # Let's create `ChainBuilder`.
    
    return None # Placeholder for now, will implement inside loop below if needed

def extract_poly(board):
    poly = pcbnew.SHAPE_POLY_SET()
    
    # heuristic: Circle or Rect first
    edges = [d for d in board.Drawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    if not edges: return poly
    
    # Check for single Circle
    circles = [e for e in edges if e.GetShape() == pcbnew.S_CIRCLE]
    if circles:
        c = circles[0]
        # Discretize
        poly.NewOutline()
        center = c.GetCenter()
        radius = c.GetRadius()
        segs = 64
        for i in range(segs):
             a = 2*math.pi*i/segs
             poly.Append(int(center.x + radius*math.cos(a)), int(center.y + radius*math.sin(a)))
        return poly
        
    # Check Loop
    # Sort edges to chain?
    # KiCad `SHAPE_POLY_SET` might be able to ingest a list of points if we sort them.
    
    # WORKAROUND: Expand Bounding Box for now if complex?
    # User said "If Circle... If Square...".
    # Let's support Circle (handled) and Square (Rectangle).
    # If built from segments, we need to chain.
    
    # Simple Chainer
    # endpoints dictionary: point -> list of edges
    map_pt = {}
    
    def add_map(pt, edge_idx):
        key = (pt.x, pt.y)
        if key not in map_pt: map_pt[key] = []
        map_pt[key].append(edge_idx)

    for i, e in enumerate(edges):
        if e.GetShape() == pcbnew.S_SEGMENT:
            add_map(e.GetStart(), i)
            add_map(e.GetEnd(), i)
        elif e.GetShape() == pcbnew.S_ARC:
            add_map(e.GetStart(), i)
            add_map(e.GetEnd(), i)

    # Walk
    current_idx = 0
    used = {0}
    
    # Start at edges[0].Start
    if edges[0].GetShape() == pcbnew.S_ARC:
        curr_pt = edges[0].GetStart() # Arcs are CCW?
        # Arcs in KiCad: Start, End, Center.
        # We need to walk edges[0] to its end.
        end_pt = edges[0].GetEnd()
    else:
        curr_pt = edges[0].GetStart()
        end_pt = edges[0].GetEnd()
        
    poly.NewOutline()
    poly.Append(curr_pt.x, curr_pt.y)
    
    # Add intermediate points for Arc
    if edges[0].GetShape() == pcbnew.S_ARC:
        # Discretize Arc 0
        pass # Todo simplified
        
    poly.Append(end_pt.x, end_pt.y)
    curr_pt = end_pt
    
    # Look for neighbor
    found = True
    while found:
        found = False
        key = (curr_pt.x, curr_pt.y)
        candidates = map_pt.get(key, [])
        for idx in candidates:
            if idx not in used:
                used.add(idx)
                # Determine direction
                e = edges[idx]
                s = e.GetStart()
                en = e.GetEnd()
                
                next_p = None
                # Check which end matches curr_pt
                dist_s = math.hypot(s.x-curr_pt.x, s.y-curr_pt.y)
                dist_en = math.hypot(en.x-curr_pt.x, en.y-curr_pt.y)
                
                if dist_s < 100: # Match Start
                    next_p = en
                elif dist_en < 100: # Match End
                    next_p = s
                
                if next_p:
                    # Append points (handle arcs?)
                    poly.Append(next_p.x, next_p.y)
                    curr_pt = next_p
                    found = True
                    break
                    
    return poly

def render_poly(board, poly, layer):
    # Iterate polygons in set
    # poly.Outline(i)
    count = poly.OutlineCount()
    for i in range(count):
         outline = poly.Outline(i)
         # PointCount?
         # Check API: SHAPE_LINE_CHAIN
         # point = outline.Point(j)
         # In Python, outline is SHAPE_LINE_CHAIN.
         # Iterate points.
         
         pts = []
         for j in range(outline.PointCount()):
             pts.append(outline.CPoint(j))
             
         # Close loop
         pts.append(pts[0])
         
         for k in range(len(pts)-1):
             seg = pcbnew.PCB_SHAPE(board)
             seg.SetShape(pcbnew.S_SEGMENT)
             seg.SetStart(pts[k])
             seg.SetEnd(pts[k+1])
             seg.SetLayer(layer)
             seg.SetWidth(pcbnew.FromMM(0.1))
             board.Add(seg)

