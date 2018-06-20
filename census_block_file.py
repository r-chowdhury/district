import shapefile
from shapely.geometry import shape, Polygon, MultiPolygon  # ,LineString
import sys
import embedded_graph
from array import array

from census_block import Census_Block

def write_boundary(fout, ring):
    array('d', [coord for pt in ring.coords for coord in pt]).tofile(fout)

def write_sizes(fout, sizes):
    array('L', sizes).tofile(fout)

def write_census_block(fout, blockID, population, polygon):
    array('Q', [blockID, population, len(polygon.interiors)]).tofile(fout)
    #array('L', [population, len(polygon.interiors)]).tofile(fout)
    write_sizes(fout, [len(polygon.exterior.coords)]+[len(interior.coords) for interior in polygon.interiors])
    write_boundary(fout, polygon.exterior)
    for interior in polygon.interiors:
        write_boundary(fout, interior)

def make_pts(L):
    x_coords = [L[i] for i in range(0, len(L), 2)]
    y_coords = [L[i] for i in range(1, len(L), 2)]
    return list(zip(x_coords, y_coords))

def read(filename):
    fin = open(filename, 'rb')
    counter = 0
    while True:
        header = array('Q')
        try:
            header.fromfile(fin, 3)
        except EOFError:
            break
        blockID = header[0]
        population = header[1]
        num_interiors = header[2]
        sizes = array('L')
        try:
            sizes.fromfile(fin, 1+num_interiors)
        except EOFError:
            print("sizes")
        exterior_coordinates = array('d')
        try:
            exterior_coordinates.fromfile(fin, 2*sizes[0])
        except EOFError:
            print("exterior")
        interiors = []
        for i in range(num_interiors):
            interiors.append(array('d'))
            try:
                interiors[i].fromfile(fin, 2*sizes[1+i])
            except EOFError:
                print("interior ",i)
        ext = make_pts(exterior_coordinates)
        ints = [make_pts(interior) for interior in interiors]
        yield Census_Block(counter, Polygon(ext, ints), population)
        counter += 1

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
        
