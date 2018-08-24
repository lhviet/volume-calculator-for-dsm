'''
Utilities for extent.
'''
# pylint: disable=locally-disabled
# pylint: disable=import-error
from osgeo import gdal
# pylint: enable=import-error

def tup_to_dic(tup):
    '''Convert tuple extent to dictionary extent'''
    return {
        'min_x': tup[0],
        'max_x': tup[1],
        'min_y': tup[2],
        'max_y': tup[3],
    }

def dic_to_tup(dic):
    '''Convert dictionary extent to tuple extent'''
    return (
        dic['min_x'],
        dic['max_x'],
        dic['min_y'],
        dic['max_y'],
    )

def apply_gt(geo_trans, ext, from_dic=True, to_dic=True):
    '''Apply GeoTransform to extent, mean, convert extent coordinate to georeferenced (geo_x, geo_y) location'''
    min_x, max_x, min_y, max_y = dic_to_tup(ext) if from_dic else ext

    min_x, min_y = gdal.ApplyGeoTransform(geo_trans, min_x, min_y)
    max_x, max_y = gdal.ApplyGeoTransform(geo_trans, max_x, max_y)

    if min_x > max_x:
        min_x, max_x = max_x, min_x

    if min_y > max_y:
        min_y, max_y = max_y, min_y

    tup = (min_x, max_x, min_y, max_y)

    return tup_to_dic(tup) if to_dic else tup
