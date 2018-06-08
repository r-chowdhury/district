from subprocess import call
import sys
import Voronoi_boundaries as vb

'''Format python3 do_redistrict.py [k districts] [two letter state code i.e. RI] > [output file]'''

if __name__ == '__main__':

	num_districts = sys.argv[1]
	state = sys.argv[2]

	cluster_file = open("../cluster_data/cluster_"+state, 'w+')

	call(["../do_redistrict", sys.argv[1], "../census_data/census_"+state], stdout=cluster_file)
	cluster_file.close()

	power_cells = vb.power_cells_fromfile("../cluster_data/cluster_"+state)

	def getCoords(polygon):
		return list(polygon.exterior.coords)

	coords = map(getCoords, power_cells)

	poly_file = open("../district_polygons/polygons_"+state, "w+")
	poly_file.write(str(list(coords)))
	poly_file.close()

	print("yay!")

