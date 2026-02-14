# PCB Panelizer Plugin for KiCad

![PCB PNLZR Logo](panelizer_plugin/icon.png)

A robust KiCad Action Plugin to panelize PCBs with advanced **V-Score** and **Mousebite** options.

## Features

- **Automated Grid Array**: Quickly create NxM arrays of your board.
- **V-Score Panelization**:
  - Generates V-Cut lines on the `F.Fab` layer.
  - Automatically segments lines at intersections for a clean grid.
  - Adds "VSCORE" text labels on `F.Fab` for fabrication instructions.
  - Removes original board outlines (`Edge.Cuts`) for a unified panel frame.
- **Customizable**:
  - Set Panel Width/Height.
  - Define Gap size (V-Score thickness matches gap).
  - Configurable Panel Frame thickness.
- **Validation**: Prevents panel generation if dimensions are too small.

## Installation (Recommended)

To ensure all metadata (Author, License, Icon) appears correctly in the KiCad Plugin and Content Manager:

1. Download the latest `panelizer_plugin.zip` (or zip the `panelizer_plugin` folder itself).
2. Open KiCad **Plugin and Content Manager**.
3. Click **Install from File...** at the bottom.
4. Select the zip file.

## Manual Installation

1. Copy the `panelizer_plugin` folder to your KiCad 3rdparty directory:
   - **Windows**: `Documents\KiCad\9.0\3rdparty\plugins\panelizer_plugin`
   - **Linux**: `~/.local/share/kicad/9.0/3rdparty/plugins/panelizer_plugin`
2. **Restart KiCad**.

> [!NOTE]
> Manual installation may result in missing metadata (Author/License) in the PCM UI, as KiCad only fully registers metadata during a package installation.

## Usage

1. Open your PCB layout in KiCad.
2. Click the **PCB Panelizer** icon (black/gold "PNLZR" logo) in the toolbar.
3. Configure your array and click **OK**.

## License

MIT License - Copyright (c) 2026 Navadeep

