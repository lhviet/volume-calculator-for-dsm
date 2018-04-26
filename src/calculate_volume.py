'''
Calculate volume
'''
# pylint: disable=locally-disabled
import numpy as np
from scipy.integrate import simps

import clip as c

def calculate_volume(tiff, geom):
    '''
    Calculate volume using GeoTiff and ShapeFile
    '''
    tiff_gt = tiff.GetGeoTransform()
    x_gap = abs(tiff_gt[1])
    y_gap = abs(tiff_gt[5])
    nodata= tiff.GetRasterBand(1).GetNoDataValue()

    clipped, boundary = c.clip(tiff_gt, tiff.ReadAsArray(), geom, nodata)
    min_z = np.amin(boundary)
    clipped[clipped == nodata] = min_z
    clipped -= min_z

    return simps(simps(clipped, None, x_gap), None, y_gap)[0]
