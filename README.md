# Red Relief Image Map (RRIM) Tools for ArcGIS Pro
### High‑Performance, Dependency‑Free Terrain Visualization Tools

## Overview

The RRIM Toolbox is a complete, ArcGIS Pro–native implementation of modern and classic terrain visualization techniques used in geomorphology, archaeology, hydrology, and landscape analysis.

This toolbox provides four modules:

1. **Topographic Openness (POS / NEG / Index)**
2. **Slope from DEM**
3. **Red Relief Image Map (Custom)**
4. **Red Relief Image Map (Classic)**

The toolbox is written entirely in pure Python, using only:

- ArcGIS Pro’s built‑in Python environment  
- NumPy  
- GDAL (bundled with ArcGIS Pro)

No external modules, no pip installs, no conda environments, and no RVT dependency.

---

# 1. Topographic Openness (POS / NEG / Index)

## High‑Performance, ArcGIS‑Native Implementation

This module computes **positive openness**, **negative openness**, and the **openness index** in a single tool.  
It uses a fully vectorized, dependency‑free algorithm based on published descriptions of the RVT method.

### Key Characteristics

#### Dependency‑Free Algorithm
Runs entirely inside ArcGIS Pro’s default Python environment.  
No external libraries or installations required.

#### Vectorized Horizon Scanning
The algorithm uses:

- precomputed horizon shift vectors  
- vectorized NumPy operations  
- padded DEM windows  
- multi‑directional horizon scanning  
- arctangent‑based angular openness  

This design supports efficient processing of large DEMs.

#### Dimensionality‑Safe Horizon Vectors
A guard ensures horizon vectors never collapse into invalid 1‑D arrays, improving stability and correctness.

#### Designed for Large DEMs
Optimized for high‑resolution LiDAR‑derived DEMs and tiled workflows.

---

## Parameters

| Parameter | Description |
|----------|-------------|
| **Input DEM(s)** | One or more DEM rasters or a folder of DEM tiles. |
| **Search Radius (pixels)** | Horizon scanning radius. Typical values: 50–200. |
| **Number of Directions** | 8 or 16. |
| **Output Folder** | Folder where POS/NEG/Index rasters will be written. |
| **Output NoData Value** | Default: –9999. |
| **Debug Mode** | Optional verbose logging. |

---

## Outputs

- `*_pos.tif` — Positive Openness  
- `*_neg.tif` — Negative Openness  
- `*_index.tif` — Openness Index (POS–NEG)/2  

All outputs are:

- 32‑bit float GeoTIFF  
- georeferenced  
- tiled  
- BIGTIFF‑safe  
- automatically added to the current ArcGIS Pro map  

---

# 2. Slope from DEM

Computes slope in degrees using a 3×3 Horn neighborhood kernel.

### Features

- Pure NumPy implementation  
- ArcGIS‑native  
- Smooth, high‑quality slope rasters  
- No NoData propagation issues  
- Fast and stable for large DEMs  

---

# 3. Red Relief Image Map (Custom)

## Modern RRIM Visualization Using POS, NEG, and Slope

This version blends:

- Positive Openness  
- Negative Openness  
- Slope  
- Cividis color ramp  

The result is a modern, perceptually uniform, high‑contrast visualization suitable for:

- geomorphology  
- hydrology  
- scientific visualization  
- publication‑quality figures  

### Output

- RGB GeoTIFF  
- GDAL `.aux.xml` sidecar for correct ArcGIS Pro color handling  
- No stretch applied  
- Ready for map display  

---

# 4. Red Relief Image Map (Classic)

## Traditional RRIM Visualization (Reds + Grays)

This version blends:

- Positive Openness  
- Negative Openness  
- Slope  
- Reds + Grays color ramps  

The result is the familiar red‑on‑gray visualization widely used in:

- archaeology  
- cultural resource management  
- legacy LiDAR workflows  

### Output

- RGB GeoTIFF  
- GDAL `.aux.xml` sidecar  
- No stretch applied  
- Ready for map display  

---

# Comparison: Custom vs. Classic RRIM

| Feature | Custom RRIM | Classic RRIM |
|--------|--------------|--------------|
| Color Ramp | Cividis (modern, perceptual) | Reds + Grays (traditional) |
| Inputs | POS + NEG + Slope | POS + NEG + Slope |
| Visual Style | Smooth, modern, high‑contrast | Red‑on‑gray, traditional |
| Best For | Scientific visualization, geomorphology | Archaeology, legacy workflows |
| Output | RGB GeoTIFF + aux.xml | RGB GeoTIFF + aux.xml |

---

# Installation

1. Clone or download the repository.  
2. Place the `.pyt` file and `.py` modules in a folder.  
3. Add the folder to ArcGIS Pro’s Toolbox list.  
4. Run tools directly from ArcGIS Pro.

---

# System Requirements

- ArcGIS Pro 3.x  
- Python 3.9 (ArcGIS default)  
- NumPy (included)  
- GDAL (included)  
- Windows 10/11  

---

# Citation

If you use this toolbox in research, please cite:

**Relief Visualization Toolbox (RVT)**  
Research Centre of the Slovenian Academy of Sciences and Arts  
University of Ljubljana, Faculty of Civil and Geodetic Engineering  

This toolbox is an independent implementation based on published algorithmic descriptions.

---

# License

MIT License (see LICENSE file)

---

# Author

**Darren J. Thornbrugh**  
USDA Forest Service  
Spatial Analysis & Ecological Modeling  

---

# Contributing

See CONTRIBUTING.md for guidelines.

---

# Screenshots / Examples

*(Add your openness and RRIM images here.)*