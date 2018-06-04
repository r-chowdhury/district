import shapefile
from shapely.geometry import shape, Polygon, MultiPolygon #,LineString
import sys

class Assignment_Element:
    #block_ID, center_ID, dependent_block_IDs, subpopulation, subarea
    def __init__(self, block_ID, center_ID):
        self.block_ID = block_ID
        self.center_ID = center_ID


class Census_Block:
    def __init__(self, ID, polyg, population):
        self.ID = ID
        assert type(polyg) == Polygon
        self.polygon = polyg
        self.population = population
        self.assignment_elements = []
        self.centroid_cache = None
    
    @property
    def centroid(self):
        if self.centroid_cache == None:
            self.centroid_cache = self.polygon.centroid
        return self.centroid_cache

def generator(shapefilename):
    sf = shapefile.Reader(shapefilename)
    counter = 0
    for shape_rec in sf.iterShapeRecords():
        geometry = shape(shape_rec.shape)
        assert type(geometry) in (Polygon, MultiPolygon)
        if type(geometry) == Polygon:
            yield Census_Block(counter, shape(shape_rec.shape), shape_rec.record[7])
            counter = counter + 1
        else: #MultiPolygon
            for polyg in geometry:
                yield Census_Block(counter, polyg, 0) #Assumes zero population for multipolygonal blocks
                counter = counter + 1

def build_id2census_block(shapefilename):
    id2census_block = {}
    for census_block in generator(shapefilename):
        id2census_block[census_block.ID] = census_block
    return id2census_block

if __name__ == '__main__':
    #write a file with some census block info
    if len(sys.argv) != 3:
        print("Use python3 ", sys.argv[0], "<path to shape file containing census blocks (without suffix)> <output filename>")
        exit(-1)
    shapefilename = sys.argv[1]
    output_filename = sys.argv[2]
    of = open(output_filename, 'w')
    for census_block in generator(shapefilename):
        if census_block.ID % 10000 == 0: print(census_block.ID)
        centroid = census_block.polygon.centroid
        pop = census_block.population
        if pop > 0:
            of.write(str(census_block.ID)+" "+str(centroid.x)+" "+str(centroid.y)+" "+str(pop)+"\n")
    of.close()
