import shapefile
from shapely.geometry import shape, Polygon, MultiPolygon, LinearRing  # ,LineString
import sys
from embedded_graph import EGraph
import census_block_file
import census_block
from pympler import asizeof

def union_bounds(bounds1, bounds2):
    return (min(bounds1[0],bounds2[0]),min(bounds1[1],bounds2[1]),max(bounds1[2],bounds2[2]),max(bounds1[3],bounds2[3]))

def dilate_bounds(bounds):
    xdelta, ydelta = bounds[2]-bounds[0],bounds[3]-bounds[1]
    return bounds[0]-xdelta, bounds[1]-ydelta,bounds[2]+xdelta,bounds[3]+ydelta

def shape_sizes(shapefilename):
    sf = shapefile.Reader(shapefilename)
    n, m = 0,0
    for shape_rec in sf.iterShapeRecords():
        geometry = shape(shape_rec.shape)
        polygons = [geometry] if geometry.geom_type =='Polygon' else geometry
        for polygon in polygons:
            n += 1
            m += len(polygon.exterior.coords)-1 + sum(len(interior.coords)-1 for interior in polygon.interiors)
    return m, n

if __name__ == "__main__":
    shapefilename = sys.argv[1]
    output_filename = sys.argv[2]
    of = open(output_filename, "wb")
    m, n = shape_sizes(shapefilename)
    print("preprocess_census_block.  Estimated number of edges: ", m, " Estimated number of vertices: ", n)
    sf = shapefile.Reader(shapefilename)
    graph = EGraph(int(1.1*m), int(1.1*n))
    counter = 0
    block_counter = 0
    bounds = (float('infinity'), float('infinity'),-float('infinity'),-float('infinity'))
    for shape_rec in sf.iterShapeRecords():
        if counter % 10000 == 0:
            print("preprocess_census_block ", counter)
        geometry = shape(shape_rec.shape)
        bounds = union_bounds(bounds, geometry.bounds)
        assert type(geometry) in (Polygon, MultiPolygon)
        #Exterior is cw, interiors (if any) are ccw
        if type(geometry) == Polygon:
            graph.add_region(geometry)
            census_block_file.write_census_block(of, block_counter, census_block.block_types['ordinary'], shape_rec.record[7], geometry)
            block_counter += 1
        else: # Multipolygon
            pop = shape_rec.record[7]
            block_type = census_block.block_types['multipolygon-zero' if pop == 0 else 'multipolygon-positive']
            for polygon in geometry:
                graph.add_region(polygon)
                census_block_file.write_census_block(of, block_counter, block_type, 0, polygon)
                block_counter += 1
        counter += 1
    print("number of blocks: ", counter)
    number_of_vertices_before_outer = graph.num_vertices()
    graph.find_outer()
    print("number of additional vertices: ", graph.num_vertices() - number_of_vertices_before_outer)
    dilated_bounds = dilate_bounds(bounds)
    gon = Polygon([(dilated_bounds[0],dilated_bounds[1]),(dilated_bounds[0],dilated_bounds[3]),(dilated_bounds[2],dilated_bounds[3]), (dilated_bounds[2], dilated_bounds[1])])
    for i in range(number_of_vertices_before_outer, graph.num_vertices()):
        outer, dummy_inners = graph.region_data(i)
        if LinearRing(outer).is_ccw:
            gon = gon.difference(Polygon(outer))
        else:
            assert False
            #census_block_file.write_census_block(of, block_counter, census_block.block_types['infinite'], 0, Polygon(outer))
            #block_counter += 1
    census_block_file.write_census_block(of, block_counter, census_block.block_types['infinite-region'], 0, gon)
    of.close()



'''
python3 preprocess_census_block.py /Users/klein/programming/district/data/CA_census_blocks/tabblock2010_06_pophu foo.bin
'''

    
