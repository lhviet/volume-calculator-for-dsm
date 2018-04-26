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

def clip(tiff_gt, tiff_arr, geom, no_data=-10000):
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

    # tiff_arr_shape = tiff_arr.shape
    # tiff_pxl_ext = eu.tup_to_dic((
    #     0, tiff_arr_shape[0],
    #     0, tiff_arr_shape[1],
    # ))
    geom_pts = get_pts_in_geom(geom)
    geom_ext = make_geom_ext(geom_pts)
    geom_pxl_ext = {
        k: int(v)
        for k, v in eu.apply_gt(gdal.InvGeoTransform(tiff_gt), geom_ext).items()
    }

    geom_gt = make_geom_gt(tiff_gt, geom_ext)
    geom_inv_gt = gdal.InvGeoTransform(geom_gt)

    if len(tiff_arr.shape) == 3:
        clipped_arr = tiff_arr[
            :,
            geom_pxl_ext['min_y']:geom_pxl_ext['max_y'],
            geom_pxl_ext['min_x']:geom_pxl_ext['max_x'],
        ]
    else:
        clipped_arr = tiff_arr[
            np.newaxis,
            geom_pxl_ext['min_y']:geom_pxl_ext['max_y'],
            geom_pxl_ext['min_x']:geom_pxl_ext['max_x'],
        ]

    pxls = [
        tuple(map(int, gdal.ApplyGeoTransform(geom_inv_gt, x, y)))
        for (x, y) in geom_pts
    ]

    raster_size = (
        int(geom_pxl_ext['max_x'] - geom_pxl_ext['min_x']),
        int(geom_pxl_ext['max_y'] - geom_pxl_ext['min_y']),
    )
    raster_poly = Image.new('L', raster_size, color=0x000001)
    ImageDraw.Draw(raster_poly).polygon(pxls, fill=0x000000)

    # TODO: Add error handlings for ValueError
    mask = np.fromstring(raster_poly.tobytes(), dtype=np.int8) \
        .reshape(raster_poly.im.size[1], raster_poly.im.size[0])

    clipped_arr = np.choose(mask, (clipped_arr, no_data))
    boundary_pts = [
        clipped_arr[0, y, x]
        for (x, y) in pxls
    ]

    return clipped_arr, boundary_pts

def get_pts_in_geom(geom):
    raw_pts = geom.GetGeometryRef(0)

    return np.array([
        (raw_pts.GetX(pt_ind), raw_pts.GetY(pt_ind))
        for pt_ind in range(raw_pts.GetPointCount())
    ])

def make_geom_ext(geom_pts):
    max_x, max_y = np.amax(geom_pts, 0)
    min_x, min_y = np.amin(geom_pts, 0)

    return {
        'min_x': min_x,
        'max_x': max_x,
        'min_y': min_y,
        'max_y': max_y,
    }

def make_geom_gt(base_gt, geom_ext):
    '''Make new GeoTransform for layer'''
    tmp_gt = list(base_gt)
    tmp_gt[0] = geom_ext['min_x']
    tmp_gt[3] = geom_ext['max_y']
    return tuple(tmp_gt)
