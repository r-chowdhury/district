from subprocess import call
import sys
import json
import Voronoi_boundaries as vb
import scipy.spatial as sp
import shapely.geometry as sg
import census_polygons as cp
import split_pulp as sp
import district_graph as dg
from functools import reduce

def getCoords(power_cell):

	return list(power_cell.exterior.coords)


#this function is no longer needed
def getDiffCoords(power_cell):

	diff = reduce(lambda x,y: x.difference(y), all_blocks, power_cell) #this function takes a lot of time

	print("calculated diff!")


	if (not isinstance(diff, list)):
		diff_coords = getCoords(diff)

	else: 
		diff_coords = map(getCoords, diff)

	return list(diff_coords)


def vb_helper(output_filename):
	#used to be required for read function in cb... may not be needed anymore

	C, A, assign_pairs = vb.Parse(do_redistrict_out)
	bbox = vb.find_bbox(C+A)
	G = dg.get(C, power_cells, bbox)

	return C, G



if __name__ == '__main__':

	'''Format python3 do_redistrict2.py [state abbrev]'''


	state_abbrev = sys.argv[1]

	power_cells = vb.power_cells_fromfile("./makefile_outputs/do_redistrict/"+state_abbrev)

	#C, G = vb_helper(do_redistrict_out)

	boundary_block_assignments = cp.parse_polygons(
										"./makefile_outputs/split_pulp/"+state_abbrev, #output file from split_pulp
										"./makefile_outputs/prepare_ILP/"+state_abbrev+"_blockdata", #census block boundary shapefile
										)

	all_blocks = cp.polygon_list(boundary_block_assignments)

	full_coords = map(getCoords, power_cells) #full outline of district
	#diff_coords = map(getDiffCoords, power_cells) #district with census blocks subtracted out


	poly_file = open("./binary_data/district_polygons/polygons_"+state_abbrev, "wb+")
	#poly_file.write(str(list(full_coords)))
	poly_file.write(str(list(full_coords)).encode('utf-8'))
	poly_file.close()


	district_file = open('./binary_data/census_polygons/boundary_blocks_'+state_abbrev, "wb+")
	#print(json.dumps(boundary_block_assignments), file=district_file)
	district_file.write(json.dumps(boundary_block_assignments).encode('utf-8'))
	district_file.close()

	print("yay!")

