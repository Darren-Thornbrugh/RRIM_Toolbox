# Red Relief Image Map (RRIM) Tools for ArcGIS Pro
### High‑Performance, Dependency‑Free Terrain Visualization Tools

## Overview

The RRIM Toolbox is a complete, ArcGIS Pro–native implementation of modern and classic terrain visualization techniques used in geomorphology, archaeology, hydrology, and landscape analysis.

This toolbox provides:

- **Native Topographic Openness (POS/NEG)**
- **Openness Index (POS–NEG)**
- **Slope from DEM**
- **Red Relief Image Map (Custom)**
- **Red Relief Image Map (Classic)**

The toolbox is written entirely in pure Python, using only:

- ArcGIS Pro’s built‑in Python environment  
- NumPy  
- GDAL (bundled with ArcGIS Pro)

No external modules, no pip installs, no conda environments, and no RVT dependency.

---

# 1. Native Topographic Openness (POS/NEG)

## High‑Performance, ArcGIS‑Native Implementation

This tool computes positive and negative topographic openness using a fully vectorized, dependency‑free algorithm based on published descriptions of the RVT method.

### Key Characteristics

#### 1. Dependency‑Free Algorithm
Runs entirely inside ArcGIS Pro’s default Python environment.  
No external libraries or installations required.

#### 2. Vectorized Horizon Scanning
The algorithm uses:

- precomputed horizon shift vectors  
- vectorized NumPy operations  
- padded DEM windows  
- multi‑directional horizon scanning  
- arctangent‑based angular openness  

This design supports efficient processing of large DEMs.

#### 3. Dimensionality‑Safe Horizon Vectors
A guard ensures horizon vectors never collapse into invalid 1‑D arrays, improving stability and correctness.

#### 4. Designed for Large DEMs
The implementation is optimized for high‑resolution LiDAR‑derived DEMs and tiled workflows.

---

## Parameters

| Parameter | Description |
|----------|-------------|
| **Input DEM(s)** | One or more DEM rasters or a folder of DEM tiles. |
| **Search Radius (pixels)** | Horizon scanning radius. Typical values: 50–200. |
| **Number of Directions** | 8 or 16. |
| **Output Folder** | Folder where POS/NEG rasters will be written. |
| **Output NoData Value** | Default: –9999. |
| **Debug Mode** | Optional verbose logging. |

---

## Outputs

- `*_pos.tif` — Positive Openness  
- `*_neg.tif` — Negative Openness  

Both outputs are:

- 32‑bit float GeoTIFF  
- georeferenced  
- tiled  
- BIGTIFF‑safe  
- automatically added to the current ArcGIS Pro map  

---

# 2. Openness Index (POS–NEG)

Computes the standard openness index:



\[
\text{Index} = \frac{\text{POS} - \text{NEG}}{2}
\]



### Inputs
- POS raster  
- NEG raster  
- or a folder containing POS/NEG tiles  

### Output
- Single‑band Float32 GeoTIFF  

---

# 3. Slope from DEM

Computes slope in degrees using a 3×3 neighborhood kernel.

### Features
- Pure NumPy implementation  
- ArcGIS‑native  
- Produces smooth, high‑quality slope rasters  

---

# 4. Red Relief Image Map (Custom)

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

---

# 5. Red Relief Image Map (Classic)

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

---

# 6. Comparison: Custom vs. Classic RRIM

| Feature | Custom RRIM | Classic RRIM |
|--------|--------------|--------------|
| Color Ramp | Cividis (modern, perceptual) | Reds + Grays (traditional) |
| Inputs | POS + NEG + Slope | POS + NEG + Slope |
| Visual Style | Smooth, modern, high‑contrast | Red‑on‑gray, traditional |
| Best For | Scientific visualization, geomorphology | Archaeology, legacy workflows |
| Output | RGB GeoTIFF | RGB GeoTIFF |

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