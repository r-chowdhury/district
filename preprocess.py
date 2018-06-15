import sys
import shapely.geometry as sg
from shapely.geometry.polygon import Polygon
# import state_shape
import census_block
import state_shape

def clip(polygons, boundary):
    #boundary is a multipolygon
    new_clipped = []
    for b in boundary:
        for i in range(len(polygons)):
            p = polygons[i].polygon
            if b.contains(p):
                new_clipped.append(p)
            elif p.intersects(b):
                new_clipped.append(p.intersection(b))
    return new_clipped


def get_empty_blocks(polygons, boundary):
    for b in boundary:
        empty_list = [b]
        for block in polygons:
            p = block.polygon
            new_list = []
            for d in empty_list:
                res = d.difference(p)
                if type(res) == sg.multipolygon.MultiPolygon:
                    for r in res:
                        new_list.append(r)
                else:
                    new_list.append(res)
            empty_list = new_list
    return empty_list
        

def print_blocks(polygons, filename):
    f = open(filename, "w")
    for r in polygons:
        x, y = r.exterior.xy
        for i in range(len(x)):
            f.write(str(x[i]) + "," + str(y[i]) + " ")
        f.write("\n")
    f.close()
    

def read_census(filename):
    return list(census_block.gen(filename))

def read_boundary(filename, state_abbrv):
    print("state abbrv:--"+state_abbrv+"--")
    return state_shape.read(state_abbrv, filename)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Use: python3 ",
            sys.argv[0],
            "[STATE ABBREV] [state shape file name] [polygons boundary census block filename] [output filename]",
        )
        exit(-1)
    state_abbrv = sys.argv[1]
    state_shape_filename = sys.argv[2]
    census_shape_filename = sys.argv[3] 
    output_filename = sys.argv[4]
    
    state_polygon  = read_boundary(state_shape_filename, state_abbrv)
    print("start with reading census")
    census_polygons = read_census(census_shape_filename)

    print("clipping...")
    census_polygons_clipped = clip(census_polygons, state_polygon)
    print("done")
    print("computing empty blocks...")
    empty_blocks = get_empty_blocks(census_polygons, state_polygon)
    print("done")
    
    print_blocks(census_polygons_clipped+empty_blocks, output_filename)
