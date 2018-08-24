'''
Module for `clip` function.

`clip` function is extracted from following link.
https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#clip-a-geotiff-with-shapefile
'''
# pylint: disable=locally-disabled
import numpy as np
from PIL import Image, ImageDraw
# pylint: disable=import-error
from osgeo import gdal, gdalnumeric
# pylint: enable=import-error

import extent_utils as eu

def clip(tiff_gt, tiff_arr, geom, no_data=-10000, clip_save_name='', is_clip_saved_in_png=True):
    '''
    Clip GeoTiff from `tiff_path` with ShapeFile from `shape_path`.

    Parameters
    ----------
    tiff : osgeo.gdal.Dataset
        path to `.tif` file
    shape_path : osgeo.ogr.DataSource
        path to `.shp` file
        :param clip_save_name: the name of saving clip. Empty string '' to not save. i.e. 'clipped-img'
        :param is_clip_saved_in_png: True to save in PNG (8-bit), and False to save in GeoTiff format (Float32)
    '''
    gdal.UseExceptions()

    # tiff_arr_shape = tiff_arr.shape
    # tiff_pxl_ext = eu.tup_to_dic((
    #     0, tiff_arr_shape[0],
    #     0, tiff_arr_shape[1],
    # ))
    geom_pts = get_pts_in_geom(geom)

    # Get the geo-extent of the geo polygon
    geom_ext = make_geom_ext(geom_pts)

    # Get the geo extent in pixel coordinates
    geom_pxl_ext = {
        k: int(v)
        for k, v in eu.apply_gt(gdal.InvGeoTransform(tiff_gt), geom_ext).items()
    }

    geom_gt = make_geom_gt(tiff_gt, geom_ext)
    geom_inv_gt = gdal.InvGeoTransform(geom_gt)

    tiff_shape = tiff_arr.shape

    if geom_pxl_ext['min_y'] < 0:
        geom_pxl_ext['min_y'] = 0
    if geom_pxl_ext['min_x'] < 0:
        geom_pxl_ext['min_x'] = 0
    if geom_pxl_ext['max_y'] < 0:
        geom_pxl_ext['max_y'] = 0
    if geom_pxl_ext['max_x'] < 0:
        geom_pxl_ext['max_x'] = 0

    # Extract data from dsm (tiff_arr) to the extent (clipped_arr)
    if len(tiff_shape) == 3:
        bound_tiff_y = tiff_shape[1] - 1
        bound_tiff_x = tiff_shape[2] - 1
        if geom_pxl_ext['max_y'] > bound_tiff_y:
            geom_pxl_ext['max_y'] = bound_tiff_y
        if geom_pxl_ext['max_x'] > bound_tiff_x:
            geom_pxl_ext['max_x'] = bound_tiff_x

        clipped_arr = tiff_arr[
            :,
            geom_pxl_ext['min_y']:geom_pxl_ext['max_y'] + 1,
            geom_pxl_ext['min_x']:geom_pxl_ext['max_x'] + 1,
        ]
    else:
        bound_tiff_y = tiff_shape[0] - 1
        bound_tiff_x = tiff_shape[1] - 1
        if geom_pxl_ext['max_y'] > bound_tiff_y:
            geom_pxl_ext['max_y'] = bound_tiff_y
        if geom_pxl_ext['max_x'] > bound_tiff_x:
            geom_pxl_ext['max_x'] = bound_tiff_x

        clipped_arr = tiff_arr[
            np.newaxis,
            geom_pxl_ext['min_y']:geom_pxl_ext['max_y'] + 1,
            geom_pxl_ext['min_x']:geom_pxl_ext['max_x'] + 1,
        ]

    # Convert the geo-polygon-points from geo-referenced to coordinates in Pixel (based on the extent)
    pxls = [
        tuple(map(int, gdal.ApplyGeoTransform(geom_inv_gt, x, y)))
        for (x, y) in geom_pts
    ]

    # FIXME:
    # This code make incorrect volume.
    # For example, when you have a triangle with
    # one point going outside to the map,
    # the point will be filtered and result volume will be 0.
    ext_bound_x = geom_pxl_ext['max_x'] - geom_pxl_ext['min_x']
    ext_bound_y = geom_pxl_ext['max_y'] - geom_pxl_ext['min_y']
    clipped_pxls = [
        (x, y)
        for (x, y) in pxls
        if 0 <= x <= ext_bound_x and
        0 <= y <= ext_bound_y
    ]

    if len(clipped_pxls) < 2:
        return np.array([]), []

    raster_size = (ext_bound_x + 1, ext_bound_y + 1)
    raster_poly = Image.new('L', raster_size, color=0x000001)
    ImageDraw.Draw(raster_poly).polygon(clipped_pxls, fill=0x000000)

    # TODO: Add error handlings for ValueError
    mask = np.fromstring(raster_poly.tobytes(), dtype=np.int8) \
        .reshape(raster_poly.im.size[1], raster_poly.im.size[0])

    clipped_arr = np.choose(mask, (clipped_arr, no_data))
    boundary_pts = [
        clipped_arr[0, y, x]
        for (x, y) in clipped_pxls
    ]

    ######### TESTING BEGIN
    # Save the clipped image to a PNG file
    if len(clip_save_name) > 0:
        if is_clip_saved_in_png:
            clippedData = clipped_arr.astype(np.int8)
            gdalnumeric.SaveArray(clippedData, clip_save_name + '.png', format="PNG")
        else:
            clippedData = clipped_arr.astype(np.float32)
            gdalnumeric.SaveArray(clippedData, clip_save_name + '.tif', format="GTiff")
    ######### TESTING END

    return clipped_arr, boundary_pts

def get_pts_in_geom(geom):
    '''Convert the polygon WKT to an array of coordinates'''
    raw_pts = geom.GetGeometryRef(0)

    return np.array([
        (raw_pts.GetX(pt_ind), raw_pts.GetY(pt_ind))
        for pt_ind in range(raw_pts.GetPointCount())
    ])

def make_geom_ext(geom_pts):
    '''
    Return the (geo-referenced) extent (display rectangle) of the geo polygon, i.e.,
    {
        'min_x': 14105340.903678089,
        'max_x': 14105404.27773767,
        'min_y': 4521636.9615872614,
        'max_y': 4521663.9832710894
    }
    '''
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
