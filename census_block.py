import shapefile
from shapely.geometry import shape, Point, Polygon, MultiPolygon  # ,LineString
import sys
from util import polygon_points
import census_block_file

class Assignment_Element:
    # block_ID, center_ID, dependent_block_IDs, subpopulation, subarea
    def __init__(self, block_ID, center_ID):
        self.block_ID = block_ID
        self.center_ID = center_ID

'''
   type 0: artificial census block resulting from multipolygon original census block with zero population
   type 1: artificial census block resulting from multipolygon original census block with positive population
   type 2: artificial census block representing infinite region
   type 3: artificial census block resulting from fill-in (currently none)
   type 4: artificial census block resulting from intersection with district
   types 5, ... : ordinary census block (type might specify which)
'''
block_types = {'multipolygon-zero':1, 'multipolygon-positive':2, 'infinite-region':3, 'fill-in':4,'intersection':5,'subblock':6, 'superblock':7, 'ordinary':8}


def has_original_polygon(block_type):
    return False #block_type == 4

class Census_Block:

    def __init__(self, ID, block_type, polyg, population, home_district = None):
        self.ID = ID
        self.block_type = block_type
        assert type(polyg) == Polygon
        self.polygon = polyg
        self.population = population
        self.assignment_elements = []
        self.centroid_cache = None
        if home_district != None: self.home_district = home_district

    @property
    def centroid(self):
        "If centroid not in polygon then some arbitrary point inside the block"
        if self.centroid_cache == None:
            centroid = self.polygon.centroid
            self.centroid_cache = centroid if self.polygon.contains(centroid) else self.polygon.representative_point()
        return self.centroid_cache
    
    def superblock(self, subblock_IDs):
        return Superblock(self.ID, self.polygon, subblock_IDs)
    
    def add_to_graph(self, G):
        G.add_region(self.polygon)
    
    def write(self, fout):
        census_block_file.write_census_block(fout, self.ID, self.block_type, self.population, self.polygon)

class Intersection_Block(Census_Block):
    '''This class is used for representing artificial census blocks
       derived by intersecting census block with district.
    '''
    def __init__(self, ID, polygon, original_ID):
        self.ID =  ID
        self.polygon = polygon
        assert type(original_ID)==int
        self.original_ID = original_ID
        self.population = 0
        #self.pts = polygon_points(original_polygon) & polygon_points(polygon)
    
    @property
    def block_type(self): return block_types['intersection']
    
    def add_to_graph(self, G):
        G.add_region(self.polygon) #self.original_polygon, pts = self.pts)
    
    def write(self, fout):
        census_block_file.write_census_block(fout, self.ID, self.block_type, 0, self.polygon, self.original_ID)

class Subblock(Intersection_Block):
    '''This is a kind of Intersection Block that is a substitute just for the purpose
       of computing the graph.
    '''
    @property
    def block_type(self): return block_types['subblock']

class Superblock(Census_Block):
    '''This class is used for representing an original census block
       that has been replaced by a collection of Subblocks.
    '''
    def __init__(self,ID, polygon, subblock_IDs):
        self.ID = ID
        self.block_type = block_types['superblock']
        self.polygon = polygon
        self.subblock_IDs = subblock_IDs
    
    def add_to_graph(self, G):
        pass


def gen(shapefilename):
    sf = shapefile.Reader(shapefilename)
    counter = 0
    for shape_rec in sf.iterShapeRecords():
        geometry = shape(shape_rec.shape)
        assert type(geometry) in (Polygon, MultiPolygon)
        if type(geometry) == Polygon:
            yield Census_Block(counter, shape(shape_rec.shape), shape_rec.record[7])
            counter = counter + 1
        else:  # MultiPolygon
            for polyg in geometry:
                yield Census_Block(
                    counter, polyg, 0
                )  # Assumes zero population for multipolygonal blocks
                counter = counter + 1


def build_id2census_block(shapefilename):
    id2census_block = {}
    for census_block in gen(shapefilename):
        id2census_block[census_block.ID] = census_block
    return id2census_block

'''
if __name__ == "__main__":
    # write a file with some census block info
    if len(sys.argv) != 3:
        print(
            "Use python3 ",
            sys.argv[0],
            "<path to shape file containing census blocks (without suffix)> <output filename>",
        )
        exit(-1)
    shapefilename = sys.argv[1]
    output_filename = sys.argv[2]
    of = open(output_filename, "w")
    for census_block in gen(shapefilename):
        if census_block.ID % 10000 == 0:
            print(census_block.ID)
        centroid = census_block.polygon.centroid
        pop = census_block.population
        if pop > 0:
            of.write(
                str(census_block.ID)
                + " "
                + str(centroid.x)
                + " "
                + str(centroid.y)
                + " "
                + str(pop)
                + "\n"
            )
    of.close()
'''
