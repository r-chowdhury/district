# makefile for cs2
# compileler definitions
# COMP_DUALS to compute prices
# PRINT_ANS to print flow (and prices if COMP_DUAL defined)
# COST_RESTART to be able to restart after a cost function change
# NO_ZERO_CYCLES finds an opeimal flow with no zero-cost cycles
# CHECK_SOLUTION check feasibility/optimality. HIGH OVERHEAD!

# change these to suit your system
CCOMP = clang++
#CCOMP = gcc-4
#CFLAGS = -g -DCHECK_SOLUTION -Wall
DEBUG = -g 
CFLAGS = -O3 -Wall 
CPPFLAGS = -O3 -Wall -std=c++1z
#CPPFLAGS = -g -Wall -std=c++1z
#CFLAGS = -O4 -DNDEBUG -DNO_ZERO_CYCLES
BIN=cs2 do_redistrict test_initial_centers test_redistrict test_find_weights

####
# Expecting the following folders to exist:

#   data/CA_census_blocks/tabblock2010_06_pophu 
#     -- for all states, with correct two-letters ID and number

#   makefile_outputs/{census_block, do_redistrict, prepare_ILP, split_pulp, main_script, gnuplot}
#     -- will contain output of the respective commands, under the state acronym

# command to make pdfs is "make pdfs"

OUT = makefile_outputs

# pdfs: $(OUT)/gnuplot/AL.pdf $(OUT)/gnuplot/FL.pdf $(OUT)/gnuplot/IL.pdf $(OUT)/gnuplot/NY.pdf $(OUT)/gnuplot/CA.pdf

pdfs: $(OUT)/main_script/AL.pdf $(OUT)/main_script/FL.pdf $(OUT)/main_script/IL.pdf $(OUT)/main_script/NY.pdf $(OUT)/main_script/CA.pdf

#################
################# 1. wget census data files  
#################

## get shape files from https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/...
## don't add these files directly to the repository (upload is too slow)

downloads: data/AL_census_blocks data/CA_census_blocks data/FL_census_blocks data/IL_census_blocks data/NY_census_blocks data/TX_census_blocks

data/%_census_blocks:
	wget "https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/tabblock2010_$(POPID)_pophu.zip"
	mkdir -p data/$*_census_blocks
	unzip tabblock2010_$(POPID)_pophu.zip -d data/$*_census_blocks
	rm tabblock2010_$(POPID)_pophu.zip

.PRECIOUS: data/%_census_blocks

data/AL_census_blocks $(OUT)/census_block/AL $(OUT)/prepare_ILP/AL $(OUT)/main_script/AL: POPID = 01
data/CA_census_blocks $(OUT)/census_block/CA $(OUT)/prepare_ILP/CA $(OUT)/main_script/CA: POPID = 06
data/FL_census_blocks $(OUT)/census_block/FL $(OUT)/prepare_ILP/FL $(OUT)/main_script/FL: POPID = 12
data/IL_census_blocks $(OUT)/census_block/IL $(OUT)/prepare_ILP/IL $(OUT)/main_script/IL: POPID = 17
data/NY_census_blocks $(OUT)/census_block/NY $(OUT)/prepare_ILP/NY $(OUT)/main_script/NY: POPID = 36
data/TX_census_blocks $(OUT)/census_block/TX $(OUT)/prepare_ILP/TX $(OUT)/main_script/TX: POPID = 48

# and main_script.py below depends on cb_2017_us_state_500k

shapestate_data/cb_2017_us_state_500k.shp:
	wget "http://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_state_500k.zip"
	mkdir -p shapestate_data
	unzip cb_2017_us_state_500k.zip -d shapestate_data
	rm cb_2017_us_state_500k.zip

.PRECIOUS: shapestate_data/cb_2017_us_state_500k.shp

#################
################# 2. census_block.py  
#################

$(OUT)/census_block/%: data/%_census_blocks census_block.py
	mkdir -p $(OUT)/census_block
	python3 census_block.py data/$*_census_blocks/tabblock2010_$(POPID)_pophu $@

.PRECIOUS: $(OUT)/census_block/%

#################
################# 3. do_redistrict
#################

$(OUT)/do_redistrict/%: $(OUT)/census_block/% do_redistrict
	mkdir -p $(OUT)/do_redistrict
	./do_redistrict $(DISTRICTS) $< > $@

.PRECIOUS: $(OUT)/do_redistrict/%

$(OUT)/do_redistrict/AL: DISTRICTS = 7
$(OUT)/do_redistrict/CA: DISTRICTS = 53
$(OUT)/do_redistrict/FL: DISTRICTS = 27
$(OUT)/do_redistrict/IL: DISTRICTS = 18
$(OUT)/do_redistrict/NY: DISTRICTS = 27
$(OUT)/do_redistrict/TX: DISTRICTS = 36

#################
################# 3. prepare_ILP.py
#################

$(OUT)/prepare_ILP/%: $(OUT)/do_redistrict/% data/%_census_blocks/* prepare_ILP.py
	mkdir -p $(OUT)/prepare_ILP
	python3 prepare_ILP.py data/$*_census_blocks/tabblock2010_$(POPID)_pophu $< $@
	test -s $@

.PRECIOUS: $(OUT)/prepare_ILP/%

#################
################# 4. split_pulp -- solve ILP
#################

SPLIT_PULP = reunification/ILP/split_pulp.py
SOLVER = gurobi

$(OUT)/split_pulp/%: $(OUT)/prepare_ILP/% $(SPLIT_PULP)
	mkdir -p $(OUT)/split_pulp
	python3 $(SPLIT_PULP) $(SOLVER) $< $@ $@.log

.PRECIOUS: $(OUT)/split_pulp/%

#################
################# 5. main_script
#################

## main_script with reunification

$(OUT)/main_script/%: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* data/%_census_blocks/* $(OUT)/split_pulp/% main_script.py
	mkdir -p $(OUT)/main_script
	python3 main_script.py $* $(OUT)/do_redistrict/$* shapestate_data/cb_2017_us_state_500k data/$*_census_blocks/tabblock2010_$(POPID)_pophu $(OUT)/split_pulp/$* $@

## with reunification

$(OUT)/main_script/%: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* data/%_census_blocks/* $(OUT)/split_pulp/% main_script.py
	mkdir -p $(OUT)/main_script
	python3 main_script.py $* $(OUT)/do_redistrict/$* shapestate_data/cb_2017_us_state_500k data/$*_census_blocks/tabblock2010_$(POPID)_pophu $(OUT)/split_pulp/$* $@


.PRECIOUS: $(OUT)/main_script/%

#################
################# 6. gnuplot (with reunification)
#################

# todo? modify main_script to accept gnuplot output file,
# or modify so gnuplot outputs on stdout,
# so we can put the gnuplot output files in a separate directory?

# $(OUT)/gnuplot/%.pdf: $(OUT)/main_script/%
$(OUT)/main_script/%.pdf: $(OUT)/main_script/%
	mkdir -p $(OUT)/gnuplot
	gnuplot	$<

# generate_images_IL:
# 	python3 main_script.py IL cluster_data/IL_do_redistrict shapestate_data/cb_2017_us_state_500k. census_data/IL_census ILP_data/IL_output_ILP gnuplot_data/IL_gnuplot
# 	python3 main_script.py IL cluster_data/IL_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/IL_gnuplotnoreunification
# 	gnuplot	gnuplot_data/IL_gnuplot 
# 	gnuplot	gnuplot_data/IL_gnuplot_noreunification

#################
################# 0. COMPILATION
#################

clean:
	rm -f $(BIN) *.o *~

rand_float.o: rand_float.cpp rand_float.hpp
	$(CCOMP) $(CPPFLAGS) -c rand_float.cpp

point.o: point.cpp point.hpp
	$(CCOMP) $(CPPFLAGS) -c point.cpp

rand_point.o: rand_point.cpp rand_point.hpp
	$(CCOMP) $(CPPFLAGS) -c rand_point.cpp

initial_centers.o: initial_centers.cpp initial_centers.hpp
	$(CCOMP) $(CPPFLAGS) -c initial_centers.cpp

test_initial_centers.o: test_initial_centers.cpp initial_centers.hpp
	$(CCOMP) $(CPPFLAGS) -c test_initial_centers.cpp

test_initial_centers: test_initial_centers.o initial_centers.o point.o
	$(CCOMP) $(CPPFLAGS) test_initial_centers.o initial_centers.o point.o -o test_initial_centers

mincostflow.o: mincostflow.cpp mincostflow.hpp build_graph.h types_cs2.h assignment.hpp
	$(CCOMP) $(CFLAGS) -c mincostflow.cpp

redistrict.o: redistrict.cpp redistrict.hpp point.hpp assignment.hpp
	$(CCOMP) $(CPPFLAGS) -c redistrict.cpp

print_out_solution.o: print_out_solution.cpp
	$(CCOMP) $(CPPFLAGS) -c print_out_solution.cpp

test_redistrict.o: test_redistrict.cpp redistrict.hpp rand_point.hpp
	$(CCOMP) $(CPPFLAGS) -c test_redistrict.cpp

do_redistrict.o: do_redistrict.cpp redistrict.hpp
	$(CCOMP) $(CPPFLAGS) -c do_redistrict.cpp

test_redistrict: test_redistrict.o redistrict.o initial_centers.o  mincostflow.o check_weights.o point.o rand_point.o rand_float.o
	$(CCOMP) $(CPPFLAGS) test_redistrict.o redistrict.o initial_centers.o mincostflow.o check_weights.o rand_point.o point.o rand_float.o -o test_redistrict

do_redistrict: do_redistrict.o redistrict.o initial_centers.o  mincostflow.o check_weights.o rand_point.o rand_float.o point.o print_out_solution.o
	$(CCOMP) $(CPPFLAGS) do_redistrict.o redistrict.o initial_centers.o mincostflow.o check_weights.o rand_point.o point.o print_out_solution.o rand_float.o -o do_redistrict

find_weights.hpp: point.hpp

find_weights.o: find_weights.cpp find_weights.hpp
	$(CCOMP) $(CPPFLAGS) -c find_weights.cpp

test_find_weights.o: test_find_weights.cpp find_weights.hpp
	$(CCOMP) $(CPPFLAGS) -c test_find_weights.cpp

test_find_weights: test_find_weights.o find_weights.o point.o
	$(CCOMP) $(CPPFLAGS) test_find_weights.o find_weights.o point.o -o test_find_weights

test_mincostflow.o: test_mincostflow.cpp mincostflow.hpp
	$(CCOMP) $(CPPFLAGS) -c test_mincostflow.cpp

test_mincostflow: test_mincostflow.o mincostflow.o point.o
	$(CCOMP) $(CPPFLAGS) test_mincostflow.o mincostflow.o point.o -o test_mincostflow

mincostflow.hpp: assignment.hpp types_cs2.h

point.hpp: rand_float.hpp

print_out_solution.hpp: assignment.hpp

rand_point.hpp: point.hpp

redistrict.hpp: assignment.hpp point.hpp

initial_centers.hpp: point.hpp
