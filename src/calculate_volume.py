'''
Calculate volume
'''
# pylint: disable=locally-disabled
import numpy as np
from scipy.integrate import simps

import clip as c

def calculate_volume(tiff, geom, clip_save_name='', is_clip_saved_in_png=True):
    '''
    Calculate volume using GeoTiff and ShapeFile
    '''
    tiff_gt = tiff.GetGeoTransform()
    x_gap = abs(tiff_gt[1])
    y_gap = abs(tiff_gt[5])
    nodata= tiff.GetRasterBand(1).GetNoDataValue()

    clipped, boundary = c.clip(tiff_gt, tiff.ReadAsArray(), geom, nodata, clip_save_name, is_clip_saved_in_png)

    # pylint: disable=len-as-condition
    if len(clipped) == 0:
        return 0, 0, 0
    # pylint: enable=len-as-condition

    reference_z = np.amin(boundary)
    clipped[clipped == nodata] = reference_z
    clipped -= reference_z

    cut = clipped.copy()
    cut[cut < 0] = 0

    fill = clipped.copy()
    fill[fill > 0] = 0

    cut_volume = simps(simps(cut, None, x_gap), None, y_gap)[0]
    fill_volume = simps(simps(fill, None, x_gap), None, y_gap)[0]
    volume = cut_volume + fill_volume

    return cut_volume, fill_volume, volume
