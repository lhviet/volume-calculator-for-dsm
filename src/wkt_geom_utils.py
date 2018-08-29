from osgeo import ogr, osr  # pylint: disable=import-error

def make_wkt_geom(dsm_gdal_dataset, wkt_string, wkt_proj = 3857):
    '''
    Detect DSM GeoTiff projection system and compare with wkt_proj.
    If they are in same projection system, do nothing.
    Else, convert the WKT to the same projection system with the DSM GeoTiff
    '''
    source = osr.SpatialReference()
    source.ImportFromEPSG(wkt_proj)

    target = osr.SpatialReference()
    target.ImportFromWkt(dsm_gdal_dataset.GetProjection())

    if source.IsSame(target):
        return ogr.CreateGeometryFromWkt(wkt_string)

    transform = osr.CoordinateTransformation(source, target)
    wkt_polygon_geom = ogr.CreateGeometryFromWkt(wkt_string)
    wkt_polygon_geom.Transform(transform)
    return wkt_polygon_geom
