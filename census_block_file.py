import shapefile
from shapely.geometry import shape, Polygon, MultiPolygon  # ,LineString
import sys
import embedded_graph
from array import array
import census_block

def write_boundary(fout, ring):
    array('d', [coord for pt in ring.coords for coord in pt]).tofile(fout)

def write_sizes(fout, sizes):
    array('L', sizes).tofile(fout)

def write_census_block(fout, blockID, block_type, population, polygon, home_district=None):
    array('L', [blockID, block_type, population, len(polygon.interiors), home_district+1 if home_district != None else 0]).tofile(fout)
    write_sizes(fout, [len(polygon.exterior.coords)]+[len(interior.coords) for interior in polygon.interiors])
    write_boundary(fout, polygon.exterior)
    for interior in polygon.interiors:
        write_boundary(fout, interior)

def write(fout, block):
    write_census_block(fout, block.ID, block.block_type, block.population, block.polygon, block.home_district if hasattr(block, "home_district") else None)

def make_pts(L):
    x_coords = [L[i] for i in range(0, len(L), 2)]
    y_coords = [L[i] for i in range(1, len(L), 2)]
    return list(zip(x_coords, y_coords))

#This uses block IDs from file; can use counter outside if that is preferred
#    fin = open(filename, 'rb')

def read_block(fin):
    "might throw EOFError"
    header = array('L')
    header.fromfile(fin, 5)
    blockID = header[0]
    block_type = header[1]
    population = header[2]
    num_interiors = header[3]
    home_district = header[4] - 1
    sizes = array('L')
    sizes.fromfile(fin, 1+num_interiors)
    exterior_coordinates = array('d')
    exterior_coordinates.fromfile(fin, 2*sizes[0])
    interiors = []
    for i in range(num_interiors):
        interiors.append(array('d'))
        interiors[i].fromfile(fin, 2*sizes[1+i])
    ext = make_pts(exterior_coordinates)
    ints = [make_pts(interior) for interior in interiors]
    return census_block.Census_Block(blockID, block_type, Polygon(ext, ints), population, home_district)

def read(filename):
    fin = open(filename, 'rb')
    while True:
        try:
            b = read_block(fin)
            yield b
        except EOFError:
            break

if __name__ == "__main__":
    import time
    import sys
    name = sys.argv[1]
    start_time = time.clock()
    count = 0
    for block in read(name):
        if count % 10000 == 0: print(count)
        count += 1
    print(time.clock() - start_time)
        
