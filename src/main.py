'''
Main entry point
'''
# pylint: disable=locally-disabled
# pylint: disable=import-error
from osgeo import gdal, ogr
# pylint: enable=import-error

from calculate_volume import calculate_volume

def main():
    '''Entry point function for testing'''
    tiff_path = 'example/sample00.tif'
    shape_path = 'example/sample00.shp'

    tiff = gdal.Open(tiff_path)
    shape = ogr.Open(shape_path)

    print('volume: ', calculate_volume(tiff, shape))

if __name__ == '__main__':
    main()
