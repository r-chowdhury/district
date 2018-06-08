import embedded_graph
import Voronoi_boundaries

def get(assignment_filename):
    '''returns graph and 3d locations of centers'''
    assignment_file = open(assignment_filename)
    k, n = [int(x) for x in assignment_file.readline().split()]
    C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
    G = embedded_graph.EGraph()
    bbox = Voronoi_boundaries.find_bbox(C_3D)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    for cell in cells:
        G.process_cell(cell, True) #get rid of extraneous points
    G.find_outer()
    return G, cells, C_3D
