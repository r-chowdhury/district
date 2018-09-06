from subprocess import call
import sys
import json
import Voronoi_boundaries as vb
import scipy.spatial as sp
import shapely.geometry as sg
import census_polygons as cp
from functools import reduce

def getCoords(power_cell):

	return list(power_cell.exterior.coords)


if __name__ == '__main__':

	'''Format python3 do_redistrict2.py [state abbrev] [split_pulp makefile output] [do_redistrict makefile output] [prepare_ILP makefile output]
		[district polygon output path] [census block polygon output path]''' 

	state_abbrev = sys.argv[1]

	if (len(sys.argv) == 2):
		#this assumes that this script is in the same directory as the makefile outputs
		do_redistrict_out = "./makefile_outputs/do_redistrict/"+state_abbrev
		split_pulp_out = "./makefile_outputs/split_pulp/"+state_abbrev
		crit_blocks = "./makefile_outputs/save_critical_blocks/"+state_abbrev
		prepare_ILP_out = "./makefile_outputs/prepare_ILP/"+state_abbrev+"_blockdata"
		district_polygon_path = "./binary_data/district_polygons/polygons_"+state_abbrev
		census_polygon_path = './binary_data/census_polygons/boundary_blocks_'+state_abbrev

	else:
		args = sys.argv[2:]
		do_redistrict_out = args.pop()
		split_pulp_out = args.pop()
		prepare_ILP_out = args.pop()
		district_polygon_path = args.pop()
		census_polygon_path = args.pop()

	state_abbrev = sys.argv[1]



	power_cells = vb.power_cells_fromfile(do_redistrict_out)

	boundary_block_assignments = cp.polygon_assignments(save_critical_blocks_out)
	# boundary_block_assignments = cp.parse_polygons(
	# 									split_pulp_out, #output file from split_pulp
	# 									prepare_ILP_out, #census block boundary shapefile
	# 									)

	#all_blocks = cp.polygon_list(boundary_block_assignments)

	full_coords = map(getCoords, power_cells) #full outline of district

	poly_file = open(district_polygon_path, "wb+")
	poly_file.write(str(list(full_coords)).encode('utf-8')) #stores as text but binary encoding
	#print(list(full_coords))
	poly_file.close()


	district_file = open(census_polygon_path, "wb+")
	district_file.write(json.dumps(boundary_block_assignments).encode('utf-8')) #again, binary encoding but text file
	#print(json.dumps(boundary_block_assignments))
	district_file.close()

	print("yay!")
