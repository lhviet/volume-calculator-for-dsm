# volume-calculator-for-dsm

This repository **DOES NOT INCLUDE ANY GeoTiff/ShapeFile FILES**.

## Volume calculator for GeoTiff DSM
- This program requires two data
  - 1. GeoTiff DSM for global information
  - 2. WKT (ShapeFile) for specifying where (the polygon) to calculate volume
  
## Prerequirements
- `libgdal` (or gdal library) v2.2.4

## Warning
- `pip install -r requirement` does not works well because of relation between `gdal` and `numpy`.
  You should install `numpy` manually, like `pip install numpy`.


## Algorithm
There is two main jobs in the Volume Calculator:

1. Based on the WKT string, cut a corresponding polygon from the GeoTiff data.

    The clip function is extracted from:
    
    https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#clip-a-geotiff-with-shapefile
    
2. Calculate the volume based on Simpson formula

    Ref. https://www.howtoexcel.info/Civil_Engineering/Earthwork_Volume.htm