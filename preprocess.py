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
            idi = polygons[i].ID
            if b.contains(p):
                new_clipped.append([p, idi])
            elif p.intersects(b):
                new_clipped.append([p.intersection(b), idi])
    return new_clipped


def get_empty_blocks(polygons, boundary):
    print("Nb connected components in state", len(boundary))
    nbbound = 0
    for b in boundary:
        empty_list = [b]
        i = 0
        for block in polygons:
            p = block.polygon
            new_list = []
            if(i%10000 == 0):
                print(i, "th census block/",len(polygons),
                      "   Nb new blocks:", len(empty_list),
                      "  ",
                      nbbound, "th connected component of the state/",
                      len(boundary))
            i+=1
            for d in empty_list:
                res = d.difference(p)
                if type(res) == sg.multipolygon.MultiPolygon:
                    for r in res:
                        new_list.append(r)
                else:
                    new_list.append(res)
            empty_list = new_list
        nbbound+=1
    return empty_list
        

def print_blocks(polygons, filename):
    f = open(filename, "w")
    for ru in polygons:
        # print("_-------------------------------------_")
        # print(type(r))
        r = ru[0]
        idr = ru[1]
        if(type(r) == sg.point.Point): continue
        if type(r) == sg.multipolygon.MultiPolygon:
            continue # for now because I don't know how to work out this
            for res in r :
                x, y = res.exterior.xy
                # print("-----", x, "-----", y)
                f.write(str(idr)+ " ")
                for i in range(len(x)):
                    f.write(str(x[i]) + "," + str(y[i]) + " ")
        elif type(r) == sg.polygon.Polygon:
            x, y = r.exterior.xy
            # print("-----", x, "-----", y)
            f.write(str(idr)+ " ")
            for i in range(len(x)):
                f.write(str(x[i]) + "," + str(y[i]) + " ")
        f.write("\n")
        # print("_-------------------------------------_")
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
    print("total number of census is", len(census_polygons))

    print("computing empty blocks...")
    # empty_blocks = get_empty_blocks(census_polygons, state_polygon)
    print("done")
    print("clipping...")
    census_polygons_clipped = clip(census_polygons, state_polygon)
    print("done")
    
    # print_blocks(census_polygons_clipped+empty_blocks, output_filename)
    print_blocks(census_polygons_clipped, output_filename)
