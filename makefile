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

# want intermediate dependent files to be retained even if later commands fail.
# .PRECIOUS -- not ideal because file will be retained even if after its command is interupted
# .SECONDARY -- cannot be set directly for files created by pattern rules
# Our work-around is to set .SECONDARY for _all_ files, below.

.SECONDARY:
# https://stackoverflow.com/questions/17625394/secondary-for-a-pattern-rule-with-gnu-make
# "You can use .SECONDARY with no prerequisites, this will set all intermediate targets behave as SECONDARY.

.DELETE_ON_ERROR:
# "If .DELETE_ON_ERROR is mentioned as a target anywhere in the
# makefile, then make will delete the target of a rule if it has
# changed and its recipe exits with a nonzero exit status, just as it
# does when it receives a signal. 

####
# will create the following folders (TODO: reorganize folders to be consistent):

#   data
#     -- to store large downloaded census block data
#
#   shapestate_data
#     -- to store cb_2017_us_state_500k files

#   makefile_outputs/{census_block, do_redistrict, prepare_ILP, split_pulp, main_script, gnuplot}
#     -- to contain output of the respective commands, under the state acronym

# command to make pdfs is "make pdfs"
# or e.g. "make RI" to make pdfs for RI

OUT = makefile_outputs

STATES = AL CA FL IL NY TX RI
# RI is just for testing

# for "make pdfs"

pdfs: $(STATES)

# for e.g., "make RI"

$(STATES): %: $(OUT)/main_script/%_blocks.pdf $(OUT)/main_script/%_districts.pdf

#################
################# 1. wget census data files  
#################

## get shape files from https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/...
## don't add these files directly to the repository (upload is too slow)

downloads: $(STATES:%=data/%_census_blocks)

AL_POPID = 01
CA_POPID = 06
FL_POPID = 12
IL_POPID = 17
NY_POPID = 36
TX_POPID = 48

RI_POPID = 44

$(STATES:%=data/%_census_blocks): data/%_census_blocks:
	@ rm -rf tabblock2010_$($*_POPID)_pophu.zip
	wget https://www2.census.gov/geo/tiger/TIGER2010BLKPOPHU/tabblock2010_$($*_POPID)_pophu.zip
	@ mkdir -p data/$*_census_blocks
	unzip tabblock2010_$($*_POPID)_pophu.zip -d data/$*_census_blocks
	@ rm tabblock2010_$($*_POPID)_pophu.zip
	@ test -s data/$*_census_blocks/tabblock2010_$($*_POPID)_pophu.shp

# .PRECIOUS: data/%_census_blocks

# and main_script.py below depends on cb_2017_us_state_500k

shapestate_data/cb_2017_us_state_500k.shp:
	@ rm -rf cb_2017_us_state_500k.zip
	wget http://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_state_500k.zip
	@ mkdir -p shapestate_data
	unzip cb_2017_us_state_500k.zip -d shapestate_data
	@ rm cb_2017_us_state_500k.zip
	@ test -s $@

# .PRECIOUS: shapestate_data/cb_2017_us_state_500k.shp

#################
################# 2. census_block.py  
#################

$(STATES:%=$(OUT)/census_block/%): $(OUT)/census_block/%: data/%_census_blocks census_block.py
	@ mkdir -p $(OUT)/census_block
	python3 census_block.py data/$*_census_blocks/tabblock2010_$($*_POPID)_pophu $@
	@ test -s $@

# .PRECIOUS: $(OUT)/census_block/%

#################
################# 3. do_redistrict
#################

AL_DISTRICTS = 7
CA_DISTRICTS = 53
FL_DISTRICTS = 27
IL_DISTRICTS = 18
NY_DISTRICTS = 27
TX_DISTRICTS = 36

RI_DISTRICTS = 2

$(STATES:%=$(OUT)/do_redistrict/%): $(OUT)/do_redistrict/%: $(OUT)/census_block/% do_redistrict
	@ mkdir -p $(OUT)/do_redistrict
	./do_redistrict $($*_DISTRICTS) $< > $@
	@ test -s $@

# .PRECIOUS: $(OUT)/do_redistrict/%

#################
################# 3. prepare_ILP.py
#################

$(STATES:%=$(OUT)/prepare_ILP/%): $(OUT)/prepare_ILP/%: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* data/%_census_blocks prepare_ILP.py
	@ mkdir -p $(OUT)/prepare_ILP
	python3 prepare_ILP.py $* shapestate_data/cb_2017_us_state_500k data/$*_census_blocks/tabblock2010_$($*_POPID)_pophu $< $@
	@ test -s $@

# .PRECIOUS: $(OUT)/prepare_ILP/%

#################
################# 4. split_pulp -- solve ILP
#################

SPLIT_PULP = reunification/ILP/split_pulp.py
SOLVER = gurobi

$(STATES:%=$(OUT)/split_pulp/%): $(OUT)/split_pulp/%: $(OUT)/prepare_ILP/% $(SPLIT_PULP)
	@ mkdir -p $(OUT)/split_pulp
	python3 $(SPLIT_PULP) $(SOLVER) $< $@ $@.log
	@ test -s $@

# .PRECIOUS: $(OUT)/split_pulp/%

#################
################# 5. main_script
#################

## main_script with reunification

$(STATES:%=$(OUT)/main_script/%_blocks): $(OUT)/main_script/%_blocks: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* data/%_census_blocks $(OUT)/split_pulp/% main_script.py main_plot.py
	@ mkdir -p $(OUT)/main_script
	python3 main_script.py $* $(OUT)/do_redistrict/$* shapestate_data/cb_2017_us_state_500k data/$*_census_blocks/tabblock2010_$($*_POPID)_pophu $(OUT)/split_pulp/$* $@
	@ test -s $@

# .PRECIOUS: $(OUT)/main_script/%_blocks

## main_script without reunification

$(STATES:%=$(OUT)/main_script/%_districts): $(OUT)/main_script/%_districts: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* data/%_census_blocks $(OUT)/split_pulp/% main_script.py
	@ mkdir -p $(OUT)/main_script
	python3 main_script.py $* $(OUT)/do_redistrict/$* shapestate_data/cb_2017_us_state_500k $@
	@ test -s $@

#################
################# 6. gnuplot
#################

# todo? modify main_script to accept gnuplot output file,
# or modify so gnuplot outputs on stdout,
# so we can put the gnuplot output files in a separate directory?

# $(OUT)/gnuplot/%.pdf: $(OUT)/main_script/%
$(STATES:%=$(OUT)/main_script/%_blocks.pdf) $(STATES:%=$(OUT)/main_script/%_districts.pdf): $(OUT)/main_script/%.pdf: $(OUT)/main_script/%
	@ mkdir -p $(OUT)/gnuplot
	gnuplot	$<
	@ test -s $@

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
