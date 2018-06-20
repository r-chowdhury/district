import shapefile
from shapely.geometry import shape, Polygon, MultiPolygon  # ,LineString
import sys
import embedded_graph
import census_block_file

if __name__ == "__main__":
    shapefilename = sys.argv[1]
    output_filename = sys.argv[2]
    of = open(output_filename, "wb")
    sf = shapefile.Reader(shapefilename)
    graph = embedded_graph.EGraph()
    counter = 0
    for shape_rec in sf.iterShapeRecords():
        if counter % 10000 == 0:
            print("preprocess_census_block ", counter)
        if shape_rec.record[7] > 0 or True: #population
            geometry = shape(shape_rec.shape)
            assert type(geometry) in (Polygon, MultiPolygon)
            if type(geometry) == Polygon:
                graph.add_region(geometry)
                census_block_file.write_census_block(of, int(shape_rec.record[4]), shape_rec.record[7], geometry)
            else: # Multipolygon
                for polygon in geometry:
                    graph.add_region(polygon)
                    census_block_file.write_census_block(of, 0, 0, polygon)
            counter += 1
    number_of_real_blocks = graph.num_vertices()
    print("number of real blocks: ", number_of_real_blocks)
    graph.find_outer()
    print("number of infinite regions: ", len(graph.infinite))
    for i in range(number_of_real_blocks, graph.num_vertices()):
        dummy_outer, dummy_inners = graph.region_data(i)
        census_block_file.write_census_block(of, 0, 0, Polygon(dummy_outer, dummy_inners))
        counter += 1
    of.close()
    print("number of artificial blocks:", graph.num_vertices() - number_of_real_blocks)



'''
python3 preprocess_census_block.py /Users/klein/programming/district/data/CA_census_blocks/tabblock2010_06_pophu foo.bin
'''

    
