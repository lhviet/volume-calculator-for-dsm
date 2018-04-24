'''
Main entry point
'''
# pylint: disable=locally-disabled
import numpy as np
# pylint: disable=import-error
from osgeo import gdal, ogr
# pylint: enable=import-error

import clip as c

def main():
    '''Entry point function for testing'''
    tiff_path = 'example/sample00.tif'
    shape_path = 'example/sample00.shp'

    tiff = gdal.Open(tiff_path)
    tiff_gt = tiff.GetGeoTransform()
    tiff_arr = tiff.ReadAsArray()

    band = tiff.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    x_gap = tiff_gt[1]
    y_gap = tiff_gt[4]

    shape = ogr.Open(shape_path)

    clipped = c.clip(tiff_gt, tiff_arr, shape)

    min_z = np.amin(clipped)
    print('volume: ', ((clipped - min_z)[clipped != nodata] * x_gap * y_gap).sum())

if __name__ == '__main__':
    main()
