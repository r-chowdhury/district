import census_block
import closest
import relevant_districts
import areas_of_intersection
import initial_population_assignment
import district_graph
import block_bfs
import join
import time # for debugging
import sys

def test(shapefilename, assignment_filename):
    G, cells, C_3D = district_graph.get(assignment_filename)
    def merge(x,y):
        relevant_district_items = y[1]
        district2pop = x[1]
        for item in relevant_district_items:
            item.population = district2pop[item.ID] if item.ID in district2pop else 0
        return y
    start_time = time.clock()
    L = list(census_block.gen(shapefilename))
    print("time 1 ", time.clock() - start_time)
    start_time = time.clock()
    L = list(closest.gen(L, C_3D))
    print("time 2 ", time.clock() - start_time)
    start_time = time.clock()
    L = list(relevant_districts.gen(L, G))
    print("time 3 ", time.clock() - start_time)
    start_time = time.clock()
    L = list(areas_of_intersection.gen(L, cells))
    print("time 4 ", time.clock() - start_time)
    start_time = time.clock()
    L = list(block_bfs.get(L, len(cells)))
    print("time 5 ", time.clock() - start_time)
    start_time = time.clock()
    # It might be a performance problem that the next statement materializes the whole dict
    d = {block.ID:(block, rel) for block,rel in L}
    print("time 6 ", time.clock() - start_time)
    start_time = time.clock()
    for id, pop_assignment in initial_population_assignment.gen(assignment_filename):
        if id in d:
            for item in d[id][1]:
                item.population = pop_assignment[item.ID] if item.ID in pop_assignment else 0
            yield d[id]
    print("time 7 ", time.clock() - start_time)
            
    ####it = join.gen(merge, initial_population_assignment.gen(assignment_filename), lambda x:x[0], iter(census_block_plus_collection), lambda x:x[0].ID)
    #for x in join.gen(merge, initial_population_assignment.gen(assignment_filename), lambda x:x[0],
    #                      census_block_dependents.gen(areas_of_intersection.gen((relevant_districts.gen(closest.gen(census_block.gen(shapefilename), C_3D), G)), cells), centers_2D), lambda x:x[0].ID):
#    for x in it:
#        yield x


args = sys.argv[1:]
shapefilename = args.pop(0)
assignment_filename = args.pop(0)
output_filename = args.pop(0)
fout = open(output_filename, 'w')
counter = 0
for census_block, relevant_district_items in test(shapefilename, assignment_filename):
    if counter % 10000 == 0: print("counter", counter)
    counter = counter + 1
    fout.write(str(census_block.ID)+" ")
    for item in relevant_district_items:   #district, area, dependent in zip(relevant_districts, areas, dependents):
        for value in [item.ID, item.population, item.area, item.dependee]:
            fout.write(str(value)+" ")
    fout.write("\n")
    fout.flush() #for debugging
fout.close()

#/Users/klein/drive/District_data/RhodeIsland_census_block_data/tabblock2010_44_pophu /Users/klein/drive/District_data/RI_new_assignment.txt foo.txt
