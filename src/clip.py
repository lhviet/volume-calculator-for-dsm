'''
Module for `clip` function.

`clip` function is extracted from following link.
https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#clip-a-geotiff-with-shapefile
'''
# pylint: disable=locally-disabled
import numpy as np
from PIL import Image, ImageDraw
# pylint: disable=import-error
from osgeo import gdal
# pylint: enable=import-error

import extent_utils as eu

def clip(tiff_gt, tiff_arr, shape, no_data=-10000):
    '''
    Clip GeoTiff from `tiff_path` with ShapeFile from `shape_path`.

    Parameters
    ----------
    tiff : osgeo.gdal.Dataset
        path to `.tif` file
    shape_path : osgeo.ogr.DataSource
        path to `.shp` file
    '''
    gdal.UseExceptions()

    # TODO: Check shape.GetLayerNumber()
    lyr = shape.GetLayer()

    # tiff_arr_shape = tiff_arr.shape
    # tiff_pxl_ext = eu.tup_to_dic((
    #     0, tiff_arr_shape[0],
    #     0, tiff_arr_shape[1],
    # ))
    lyr_ext = eu.tup_to_dic(lyr.GetExtent())
    lyr_pxl_ext = {
        k: int(v)
        for k, v in eu.apply_gt(gdal.InvGeoTransform(tiff_gt), lyr_ext).items()
    }

    lyr_gt = make_lyr_gt(tiff_gt, lyr_ext)
    lyr_inv_gt = gdal.InvGeoTransform(lyr_gt)

    if len(tiff_arr.shape) == 3:
        clipped_arr = tiff_arr[
            :,
            lyr_pxl_ext['min_y']:lyr_pxl_ext['max_y'],
            lyr_pxl_ext['min_x']:lyr_pxl_ext['max_x'],
        ]
    else:
        clipped_arr = tiff_arr[
            np.newaxis,
            lyr_pxl_ext['min_y']:lyr_pxl_ext['max_y'],
            lyr_pxl_ext['min_x']:lyr_pxl_ext['max_x'],
        ]

    pxls = [
        tuple(map(int, gdal.ApplyGeoTransform(lyr_inv_gt, x, y)))
        for (x, y) in get_pts_in_lyr(lyr)
    ]

    print(pxls)

    raster_size = (
        int(lyr_pxl_ext['max_x'] - lyr_pxl_ext['min_x']),
        int(lyr_pxl_ext['max_y'] - lyr_pxl_ext['min_y']),
    )
    raster_poly = Image.new('L', raster_size, color=0x000001)
    ImageDraw.Draw(raster_poly).polygon(pxls, fill=0x000000)

    # TODO: Add error handlings for ValueError
    mask = np.fromstring(raster_poly.tobytes(), dtype=np.int8) \
        .reshape(raster_poly.im.size[1], raster_poly.im.size[0])

    clipped_arr = np.choose(mask, (clipped_arr, no_data))

    return clipped_arr

def make_lyr_gt(base_gt, lyr_ext):
    '''Make new GeoTransform for layer'''
    tmp_gt = list(base_gt)
    tmp_gt[0] = lyr_ext['min_x']
    tmp_gt[3] = lyr_ext['max_y']
    return tuple(tmp_gt)

def get_pts_in_lyr(lyr):
    '''Get points in layer'''
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    raw_pts = geom.GetGeometryRef(0)

    pts = []

    for pt_ind in range(raw_pts.GetPointCount()):
        pts.append((raw_pts.GetX(pt_ind), raw_pts.GetY(pt_ind)))

    return pts
