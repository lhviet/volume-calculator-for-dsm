# volume-calculator-for-dsm

This repository **DOES NOT INCLUDE ANY GeoTiff/ShapeFile FILES**.

## Volume calculator for GeoTiff DSM
- This program requires two data
  - 1. GeoTiff DSM for global information
  - 2. ShapeFile for specifying where to calculate volume
  
## Prerequirements
- `libgdal` (or gdal library) v2.2.4

## Warning
- `pip install -r requirement` does not works well because of relation between `gdal` and `numpy`.
  You should install `numpy` manually, like `pip install numpy`.
