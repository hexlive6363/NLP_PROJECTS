# makegraph.ipynb - Graph Visualization Guide

This notebook demonstrates comprehensive graph visualization capabilities using different colors, styles, markers, and themes.

## Overview

The `makegraph.ipynb` notebook contains examples of various graph types, each styled with distinct:
- **Color palettes** (viridis, coolwarm, plasma, Set1, Set2, Dark2, HUSL, custom hex colors)
- **Line styles** (solid, dashed, dash-dot, dotted)
- **Markers** (circles, squares, triangles, diamonds)
- **Transparency levels**
- **Edge colors and borders**
- **Grid styles**

## Graph Types Included

### 1. Bar Plots
- Single bar plots with viridis and custom hex color palettes
- Grouped bar plots with three series showing different colors
- Multiple bar plots with seaborn palettes (Set1, Dark2, HUSL, custom)

### 2. Line Plots
- Multiple line series with different line styles: `-` (solid), `--` (dashed), `-.` (dash-dot), `:` (dotted)
- Various markers: `o` (circle), `s` (square), `^` (triangle), `D` (diamond)
- Custom colors for each series

### 3. Scatter Plots
- Color gradients using continuous colormaps (coolwarm, plasma)
- Variable point sizes
- Semi-transparent points with edge colors

### 4. Seaborn Statistical Plots
- Box plots with Set2 palette
- Violin plots with muted palette
- Bar plots with multiple seaborn color palettes

### 5. Heatmaps
- Multiple colormap options: coolwarm, RdYlGn, viridis, Blues
- Both matplotlib and seaborn implementations
- Annotated values for detailed visualization

### 6. Area Plots
- Simple area fills with transparency
- Stacked area plots with multiple layers
- Custom color combinations

### 7. Pie Charts
- Custom color palettes with hex codes
- Exploded slices for emphasis
- Shadow effects and edge borders
- Percentage annotations

### 8. Histograms
- Single and multiple overlapping histograms
- Step-style histograms
- Stacked histograms
- Various transparency and edge color options

## Color Palettes Used

### Matplotlib Colormaps
- `viridis` - perceptually uniform colormap
- `coolwarm` - blue to red diverging
- `plasma` - bright colormap
- `RdYlGn` - red-yellow-green diverging
- `Blues` - sequential blue shades
- `Set1`, `Set2`, `Set3` - qualitative color sets
- `Dark2` - darker qualitative colors
- `husl` - perceptually uniform hues
- `muted` - muted colors

### Custom Hex Colors
- `#FF6B6B` - Coral red
- `#4ECDC4` - Turquoise
- `#45B7D1` - Sky blue
- `#FFA07A` - Light salmon
- `#98D8C8` - Mint green
- `#e74c3c` - Bright red
- `#3498db` - Blue
- `#2ecc71` - Green
- `#f39c12` - Orange
- `#9b59b6` - Purple
- `#e67e22` - Carrot orange
- `#1abc9c` - Teal

## How to Use

1. **Install dependencies**:
   ```bash
   pip install matplotlib seaborn numpy pandas
   ```

2. **Run the notebook**:
   - Open `makegraph.ipynb` in Jupyter Notebook or JupyterLab
   - Execute cells sequentially
   - All graphs will be displayed inline

3. **Customize**:
   - Modify color values in the code
   - Change line styles, markers, or other parameters
   - Adapt the sample data to your needs

## Features

- **24 total cells**: 13 code cells + 11 markdown cells
- **9 categories** of visualizations
- **Multiple color schemes** per graph type
- **Professional styling** with proper labels, legends, and grids
- **Educational comments** explaining each visualization

## Requirements

```
matplotlib >= 3.0
seaborn >= 0.11
numpy >= 1.19
pandas >= 1.0
```

## Notes

- All plots use different styling to showcase variety
- Transparency (alpha) values range from 0.5 to 0.8 for better visibility
- Grid styles vary between dashed, dotted, and solid with different alpha values
- Each graph includes proper titles, axis labels, and legends
- Sample data is randomly generated for demonstration purposes

## Examples of Different Styles

### Line Styles
- `-` : Solid line
- `--` : Dashed line  
- `-.` : Dash-dot line
- `:` : Dotted line

### Markers
- `o` : Circle
- `s` : Square
- `^` : Triangle (up)
- `D` : Diamond
- `v` : Triangle (down)
- `*` : Star

### Edge Colors
- `'black'`, `'navy'`, `'white'` for borders
- Various linewidth values (0.5 to 2.5)

This notebook serves as a comprehensive reference for creating visually distinct and professional-looking graphs in Python!
