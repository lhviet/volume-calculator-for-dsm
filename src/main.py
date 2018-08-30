'''
Main entry point
'''
import sys
import hashlib

# pylint: disable=locally-disabled
from osgeo import gdal # pylint: disable=import-error

from calculate_volume import calculate_volume
from wkt_geom_utils import make_wkt_geom

def main(argv):
    '''
    Takes 2 command line arguments and use them as `tiff_path` and `wkt_string`.
    `tiff_path` is a path to GeoTiff DSM file.
    `wkt_string` is a WKT format string (which describes shape of area for integration)
    This prints result as `volume: {result vaule}` format.
    '''
    tiff_path = '../example/sample00.tif'
    # shape_path = 'example/sample00.shp'
    wkt_string = 'POLYGON ((297854.531508583 4162781.09825457,297903.046025991 4162786.45581586,297904.401298411 4162773.53837561,297884.474558611 4162770.99723982,297884.813376716 4162767.6302349,297877.444082933 4162766.95259869,297877.041736433 4162770.29842748,297855.886781003 4162768.24434272,297854.531508583 4162781.09825457))' # pylint: disable=line-too-long

    if len(argv) == 3:
        tiff_path = argv[1]
        # shape_path = argv[2]
        wkt_string = argv[2]

    gdal.UseExceptions()
    tiff = gdal.Open(tiff_path)
    # shape = ogr.Open(shape_path)
    # lyr = shape.GetLayer()
    # feat = lyr.GetNextFeature()
    # geom = feat.GetGeometryRef()
    # print(geom.ExportToWkt())
    # print("Projection is {}".format(tiff.GetProjection()))
    geom = make_wkt_geom(tiff, wkt_string)

    m = hashlib.md5(wkt_string.encode())
    file_name = tiff_path[:(tiff_path.rfind('/') + 1)] + m.hexdigest()

    print('{ "cut": %f, "fill": %f,"volume": %f }' % calculate_volume(tiff, geom, file_name))

if __name__ == '__main__':
    main(sys.argv)
