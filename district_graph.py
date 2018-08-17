import embedded_graph
import state_shape
import Voronoi_boundaries

def find_bbox(state_abbreviation, state_boundary_shapefilename, C_3D):
    state_boundary = state_shape.read(state_abbreviation, state_boundary_shapefilename)
    L = sum((list(p.exterior.coords) for p in state_boundary), [])
    return Voronoi_boundaries.find_bbox(C_3D+L)


def get(C_3D, cells, bbox):
    '''returns graph'''
    G = embedded_graph.EGraph(6*len(cells), len(cells)+1)
    for cell in cells:
        G.add_region(cell, True) #get rid of extraneous points
    G.find_outer()
    return G
