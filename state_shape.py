import shapefile
from shapely.geometry import shape

def read(state_abbreviation, shape_filename):
    '''inputs:
         - two-letter state abbreviation, e.g. 'CA' or 'RI'
         - path to shape filename (not necessarily including suffix
       output: shapely.geometry.multipolygon.MultiPolygon
    '''
    sf = shapefile.Reader(shape_filename)
    x = next(x for x in sf.iterShapeRecords()  if x.record[4]==state_abbreviation)
    return shape(x.shape.__geo_interface__)
