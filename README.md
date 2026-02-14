# KiCad Plugin & Scripting Guide

This guide explains how KiCad plugins work and provides a step-by-step approach to building a PCB panelization plugin with mousebites (break-tabs).

## 1. KiCad Plugin Architecture

KiCad's PCB editor (`pcbnew`) has a powerful Python scripting API. Plugins integrate into the GUI (usually under the "Tools" or "External Plugins" menu) to automate tasks.

### Key Concepts
- **`pcbnew` Module**: The core Python module that gives access to the board, modules (footprints), tracks, and drawings.
- **`ActionPlugin` Class**: The base class for creating plugins that appear in the KiCad menu. You inherit from this class and override the `Run()` method.
- **`Scripting Console`**: A built-in Python console in Pcbnew (Tools > Scripting Console) useful for testing code snippets interactively.

### Structure of a Plugin
A typical plugin consists of:
1.  **`__init__.py`**: Makes the directory a Python package (often just imports the main plugin class).
2.  **`plugin_file.py`**: Contains the plugin class and logic.
3.  **Metadata**: (Optional) `metadata.json` for the Plugin and Content Manager (PCM).

For simple local plugins, a single `.py` file describing the `ActionPlugin` works too, but a folder structure is recommended.

## 2. Installation Locations

To install a plugin, copy your plugin folder or file to the KiCad scripting directory.

| OS | Path |
| :--- | :--- |
| **Windows** | `%USERPROFILE%\Documents\KiCad\8.0\scripting\plugins` |
| **Linux** | `~/.local/share/kicad/8.0/scripting/plugins` |
| **macOS** | `~/Documents/KiCad/8.0/scripting/plugins` |

*(Replace `8.0` with your specific KiCad version, e.g., `7.0`)*

## 3. Panelization Logic

Panelization involves creating an array of your board design to manufacture multiple copies at once.

### Steps:
1.  **Load Board**: Access the currently open board via `pcbnew.GetBoard()`.
2.  **Get Boundary**: Find the implementation of the board edges (`Edge.Cuts` layer).
3.  **Step and Repeat**: Loop through rows/cols and copy all board items (tracks, pads, text, drawings) to new coordinates.
4.  **Handling Nets**: KiCad components need unique references. You may need to update references (e.g., `R1` -> `R1_Panel2`) to avoid connectivity issues, or keep them same if just drawing geometry (less safe for DRC).

## 4. Mousebites (Break-tabs) Logic

Mousebites are weak points connecting the PCBs to the panel frame, allowing you to snap them apart.

### Anatomy of a Mousebite:
1.  **Tab**: A small bridge of PCB material ( FR4) connecting two boards or a board to a frame. Created by **interrupting the board outline** (Edge.Cuts).
2.  **Perforations**: A line of unplated holes (drill hits) across the tab to weaken it.

### Implementation Strategy:
1.  **Draw Outline**: Instead of a continuous rectangle for the board edge, draw the edge segments *skipping* the tab width.
2.  **Draw Tab**: Draw the tab lines connecting the boards.
3.  **Add Holes**: Place `PCB_VIA` or pad objects with `Drill` size (e.g., 0.5mm) and specific spacing (e.g., 0.8mm pitch) across the tab area.

## 5. Starter Code

See the accompanying `panelize_plugin.py` for a working example of a plugin that duplicates the board and adds mousebites.
