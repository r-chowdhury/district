import sys
import json
import shapefile
import scipy.spatial as sp
import shapely.geometry as sg
import census_block as cb
import census_block_file as cbf
import split_pulp as sp
import prepare_ILP as prep
import closest_kd
import relevant_districts
import census_block_district_intersection



def prepare_ILP(args):
	state_abbreviation = args[0]
	state_boundary_shapefilename = args[1]
	shapefilename = args[2]
	assignment_filename = args[3]
	output_filename = 'prep_tmp'
	fout = open(output_filename, 'w')
	counter = 0
	for census_block, relevant_district_items in prep.test(state_abbreviation, state_boundary_shapefilename, shapefilename, assignment_filename):
		if counter % 10000 == 0: print("counter", counter)
		counter = counter + 1
		fout.write(str(census_block.ID)+" ")
		for item in relevant_district_items:   #district, area, dependent in zip(relevant_districts, areas, dependents):
			for value in [item.ID, item.population, item.area, item.dependee]:
				fout.write(str(value)+" ")
		fout.write("\n")
		fout.flush() #for debugging
	fout.close()


def parse_polygons(split_pulp_out, blockdata_filename):
	#C aka C_3D
	#G is an output of a the function from district_graph.py method get(), necessary for generating proper list of census blocks
	f = open(split_pulp_out, "r")
	lines = f.readlines()

	#L becomes the list of all census blocks
	L = list(cbf.read(blockdata_filename))
	#L = list(closest_kd.gen(L, C))
	#L = list(relevant_districts.gen(L, G))
	#L = list(census_block_district_intersection.gen(L, power_cells, len(L)))

	polygons = {}
	print(len(L))
	counter = 0

	for line in lines:
		items = line.split()
		ID = int(items[0]) #gets ID of census block
		assignment = int(items[1]) #gets district assignment of census block
		if (int(ID) < len(L)):
			polygon = list(L[int(ID)].polygon.exterior.coords) #gets polygon of boundary census block

			if assignment not in polygons:
				polygons[assignment] = [polygon]
				counter += 1
			else:
				polygons[assignment].append(polygon)
				counter += 1

	print(counter)
	return polygons


def polygon_list(polygons):

	all_polygons = []

	for k in polygons:
		all_polygons.extend(polygons[k])

	polygon_list = map(lambda x : sg.Polygon(x), all_polygons)

	return list(polygon_list)



def compute_ILP(args):

	prepare_ILP(args)
	with open('prep_tmp') as input:
		assignment = sp.pulp_assign('gurobi', input)

	with open('output_tmp', 'w+') as output:
		for b in sorted(assignment.keys()):
			print(b, assignment[b], file=output)

	polygons = parse_polygons('output_tmp', args[2])

	return polygons



if __name__ == '__main__':
	'''Format: python3 census_polygons.py [state abbrev] [census block shapefile]'''

	state_abbrev = sys.argv[1]
	census_block_shapefile = sys.argv[2]

	polygons = compute_ILP([state_abbrev, './shapestate_data/cb_2017_us_state_500k.shp', census_block_shapefile, './cluster_data/cluster_'+state_abbrev])

	print(polygons)

	polygon_list(polygons)

