#!/usr/bin/env python3

# import numpy as np
# import matplotlib.pyplot as plt
import sys

# import scipy.spatial as sp
# import shapely.geometry as sg
# from shapely.geometry.polygon import Polygon
# from matplotlib import colors as mcolors
import Voronoi_boundaries as vb
import main_plot as mplot

if __name__ == "__main__":
    if len(sys.argv) == 7:
        state_abbreviation = sys.argv[1]
        C_3D, A, assign_pairs, bbox = vb.Parse(sys.argv[2])
        power_cells = vb.power_cells_fromfile(sys.argv[2])
        # mplot.plot_helperVoronoi(C_3D, A, assign_pairs, bbox,
        #                          sys.argv[5]+"voronoi")
        mplot.plot_helperGNUplot(
            C_3D,
            A,
            power_cells,
            bbox,
            state_abbreviation,
            sys.argv[3],
            sys.argv[4],
            sys.argv[5],
            sys.argv[6],
        )
    elif len(sys.argv) == 5:
        state_abbreviation = sys.argv[1]
        C_3D, A, assign_pairs, bbox = vb.Parse(sys.argv[2])
        power_cells = vb.power_cells_fromfile(sys.argv[2])
        # mplot.plot_helperVoronoi(C_3D, A, assign_pairs, bbox,
        #                          sys.argv[5]+"voronoi")
        mplot.plot_helperGNUplot(
            C_3D,
            A,
            power_cells,
            bbox,
            state_abbreviation,
            sys.argv[3],
            "",
            "",
            sys.argv[4]
        )
    else:
        print(
            "Use: python3 ",
            sys.argv[0],
            "[STATE ABBREV] [output redistrict.c++ filename] [state shape file name] [polygons_boundary_census_block_filename] [assignment_boundary_census_block_filename] [output file name]",
        )
        exit(-1)

    # mplot.plot_helperGNUplot_fromfile(sys.argv[5]+"voronoi",
    #                                   sys.argv[2], "", "",
    #                                   sys.argv[5])
