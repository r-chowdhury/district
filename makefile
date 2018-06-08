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
# Expecting the following folders to exists
# census_data containing the output of read_census
# cluster_data (will contain output of do_redistrict)
# ILP_data (will contain input for ILP after split_pulp and the output of
# the ILP)
# gnuplot_data (will contain output of python script for and the output of
# the gnuplot procedure)
# data/CA_census_blocks/tabblock2010_06_pophu for all states (with correct
# two-letters ID and number)

# command is make "command" STATE=<two-letters id>
# in case of run_ILP expect additional argument SOLVER=<name of solver for
# split_pulp>

do_all_steps_AL: run_redistrict_AL run_prepare_ILP_AL run_ILP_AL generate_images_AL
do_all_steps_FL: run_redistrict_FL run_prepare_ILP_FL run_ILP_FL generate_images_FL
do_all_steps_IL: run_redistrict_IL run_prepare_ILP_IL run_ILP_IL generate_images_IL
do_all_steps_NY: run_redistrict_NY run_prepare_ILP_NY run_ILP_NY generate_images_NY
do_all_steps_CA: run_redistrict_CA run_prepare_ILP_CA run_ILP_CA generate_images_CA
do_all_steps_TX: run_redistrict_TX run_prepare_ILP_TX run_ILP_TX generate_images_TX

run_redistrict : run_redistrict_$(STATE)

run_redistrict_all: run_redistrict_AL run_redistrict_FL run_redistrict_IL run_redistrict_NY run_redistrict_TX run_redistrict_CA

run_redistrict_AL:
	./do_redistrict 7 census_data/AL_census > cluster_data/AL_do_redistrict
run_redistrict_FL:
	./do_redistrict 27 census_data/FL_census > cluster_data/FL_do_redistrict
run_redistrict_IL:
	./do_redistrict 18 census_data/IL_census > cluster_data/IL_do_redistrict
run_redistrict_NY:
	./do_redistrict 27 census_data/NY_census > cluster_data/NY_do_redistrict
run_redistrict_CA:
	./do_redistrict 53 census_data/CA_census > cluster_data/CA_do_redistrict
run_redistrict_TX:
	./do_redistrict 36 census_data/TX_census > cluster_data/TX_do_redistrict

run_prepare_ILP_all: run_prepare_ILP_AL run_prepare_ILP_FL run_prepare_ILP_IL run_prepare_ILP_NY run_prepare_ILP_TX run_prepare_ILP_CA

run_prepare_ILP: run_prepare_ILP_$(STATE)

run_prepare_ILP_AL:
	python3 prepare_ILP.py data/AL_census_blocks/tabblock2010_01_pophu  cluster_data/AL_do_redistrict ILP_data/AL_input_ILP
run_prepare_ILP_CA:
	python3 prepare_ILP.py data/CA_census_blocks/tabblock2010_06_pophu  cluster_data/CA_do_redistrict ILP_data/CA_input_ILP
run_prepare_ILP_FL:
	python3 prepare_ILP.py data/FL_census_blocks/tabblock2010_12_pophu  cluster_data/FL_do_redistrict ILP_data/FL_input_ILP
run_prepare_ILP_IL:
	python3 prepare_ILP.py data/IL_census_blocks/tabblock2010_17_pophu  cluster_data/IL_do_redistrict ILP_data/IL_input_ILP
run_prepare_ILP_NY:
	python3 prepare_ILP.py data/NY_census_blocks/tabblock2010_36_pophu  cluster_data/NY_do_redistrict ILP_data/NY_input_ILP
run_prepare_ILP_TX:
	python3 prepare_ILP.py data/TX_census_blocks/tabblock2010_48_pophu  cluster_data/TX_do_redistrict ILP_data/TX_input_ILP

run_ILP_all: run_ILP_AL run_ILP_FL run_ILP_IL run_ILP_NY run_ILP_CA run_ILP_TX

run_ILP : run_ILP_$(STATE)

run_ILP_AL:
	python3 reunification/ILP/split_pulp.py $(SOLVER) ILP_data/AL_input_ILP ILP_data/AL_output_ILP ILP_data/AL_log_ILP
run_ILP_FL:
	python3 reunification/ILP/split_pulp.py $(SOLVER) ILP_data/FL_input_ILP ILP_data/FL_output_ILP ILP_data/FL_log_ILP
run_ILP_IL:
	python3 reunification/ILP/split_pulp.py $(SOLVER) ILP_data/IL_input_ILP ILP_data/IL_output_ILP ILP_data/IL_log_ILP
run_ILP_NY:
	python3 reunification/ILP/split_pulp.py $(SOLVER) ILP_data/NY_input_ILP ILP_data/NY_output_ILP ILP_data/NY_log_ILP
run_ILP_CA:
	python3 reunification/ILP/split_pulp.py $(SOLVER) ILP_data/CA_input_ILP ILP_data/CA_output_ILP ILP_data/CA_log_ILP
run_ILP_TX:
	python3 reunification/ILP/split_pulp.py $(SOLVER) ILP_data/TX_input_ILP ILP_data/TX_output_ILP ILP_data/TX_log_ILP


generate_images_all: generate_images_AL generate_images_FL generate_images_IL generate_images_NY generate_images_CA generate_images_TX

generate_images : generate_images_$(STATE)

generate_images_AL:
	python3 main_script.py AL cluster_data/AL_do_redistrict shapestate_data/cb_2017_us_state_500k. census_data/AL_census ILP_data/AL_output_ILP gnuplot_data/AL_gnuplot
	python3 main_script.py AL cluster_data/AL_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/AL_gnuplotnoreunification
	gnuplot	gnuplot_data/AL_gnuplot 
	gnuplot	gnuplot_data/AL_gnuplot_noreunification

generate_images_FL:
	python3 main_script.py FL cluster_data/FL_do_redistrict shapestate_data/cb_2017_us_state_500k. census_data/FL_census ILP_data/FL_output_ILP gnuplot_data/FL_gnuplot
	python3 main_script.py FL cluster_data/FL_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/FL_gnuplotnoreunification
	gnuplot	gnuplot_data/FL_gnuplot 
	gnuplot	gnuplot_data/FL_gnuplot_noreunification

generate_images_IL:
	python3 main_script.py IL cluster_data/IL_do_redistrict shapestate_data/cb_2017_us_state_500k. census_data/IL_census ILP_data/IL_output_ILP gnuplot_data/IL_gnuplot
	python3 main_script.py IL cluster_data/IL_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/IL_gnuplotnoreunification
	gnuplot	gnuplot_data/IL_gnuplot 
	gnuplot	gnuplot_data/IL_gnuplot_noreunification

generate_images_NY:
	python3 main_script.py NY cluster_data/NY_do_redistrict shapestate_data/cb_2017_us_state_500k. census_data/NY_census ILP_data/NY_output_ILP gnuplot_data/NY_gnuplot
	python3 main_script.py NY cluster_data/NY_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/NY_gnuplotnoreunification
	gnuplot	gnuplot_data/NY_gnuplot 
	gnuplot	gnuplot_data/NY_gnuplot_noreunification

generate_images_CA:
	python3 main_script.py CA cluster_data/CA_do_redistrict  shapestate_data/cb_2017_us_state_500k. census_data/CA_census ILP_data/CA_output_ILP gnuplot_data/CA_gnuplot
	python3 main_script.py CA cluster_data/CA_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/CA_gnuplotnoreunification
	gnuplot	gnuplot_data/CA_gnuplot 
	gnuplot	gnuplot_data/CA_gnuplot_noreunification

generate_images_TX:
	python3 main_script.py TX cluster_data/TX_do_redistrict shapestate_data/cb_2017_us_state_500k. census_data/TX_census ILP_data/TX_output_ILP gnuplot_data/TX_gnuplot
	python3 main_script.py TX cluster_data/TX_do_redistrict shapestate_data/cb_2017_us_state_500k. gnuplot_data/TX_gnuplotnoreunification
	gnuplot	gnuplot_data/TX_gnuplot 
	gnuplot	gnuplot_data/TX_gnuplot_noreunification


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
