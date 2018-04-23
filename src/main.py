'''
Main entry point
'''
# pylint: disable=import-error
from osgeo import gdal, ogr
# pylint: enable=import-error

import clip

def main():
    '''Entry point function for testing'''
    tiff_path = 'example/sample00.tif'
    shape_path = 'example/sample00.shp'
    tiff = gdal.Open(tiff_path)
    shape = ogr.Open(shape_path)
    clip.clip(tiff, shape)

if __name__ == '__main__':
    main()
