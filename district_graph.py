import embedded_graph
import state_shape
import Voronoi_boundaries

def get(state_abbreviation, state_boundary_shapefilename, assignment_filename):
    '''returns graph and 3d locations of centers'''
    assignment_file = open(assignment_filename)
    k, n = [int(x) for x in assignment_file.readline().split()]
    C_3D = [tuple(float(x) for x in assignment_file.readline().split()) for _ in range(k)]
    G = embedded_graph.EGraph()
    state_boundary = state_shape.read(state_abbreviation, state_boundary_shapefilename)
    L = sum((list(p.exterior.coords) for p in state_boundary), [])
    bbox = Voronoi_boundaries.find_bbox(C_3D+L)
    cells = Voronoi_boundaries.power_cells(C_3D, bbox)
    for cell in cells:
        G.process_cell(cell, True) #get rid of extraneous points
    G.find_outer()
    return G, cells, C_3D
