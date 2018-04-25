'''
Calculate volume
'''
# pylint: disable=locally-disabled
import numpy as np
from scipy.integrate import simps

import clip as c

def calculate_volume(tiff, shape):
    '''
    Calculate volume using GeoTiff and ShapeFile
    '''
    tiff_gt = tiff.GetGeoTransform()
    tiff_arr = tiff.ReadAsArray()

    band = tiff.GetRasterBand(1)
    nodata = band.GetNoDataValue()
    x_gap = abs(tiff_gt[1])
    y_gap = abs(tiff_gt[5])

    lyr = shape.GetLayer()

    clipped, boundary = c.clip(tiff_gt, tiff_arr, lyr, nodata)
    min_z = np.amin(boundary)
    clipped[clipped == nodata] = min_z
    clipped -= min_z

    sub_volumes = simps(clipped, None, x_gap)
    return simps(sub_volumes, None, y_gap)[0]
