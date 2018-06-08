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

do_all_steps_AL: run_redistrict_AL run_prepare_ILP_AL run_ILP_AL generate_images_AL

run_redistrict_all: run_redistrict_AL run_redistrict_FL run_redistrict_IL run_redistrict_NY run_redistrict_TX run_redistrict_CA

run_redistrict_AL:
	./do_redistrict 7 AL_census > AL_do_redistrict
run_redistrict_FL:
	./do_redistrict 27 FL_census > FL_do_redistrict
run_redistrict_IL:
	./do_redistrict 18 IL_census > IL_do_redistrict
run_redistrict_NY:
	./do_redistrict 27 NY_census > NY_do_redistrict
run_redistrict_CA:
	./do_redistrict 53 CA_census > CA_do_redistrict
run_redistrict_TX:
	./do_redistrict 36 TX_census > TX_do_redistrict

run_prepare_ILP_all: run_prepare_ILP_AL run_prepare_ILP_FL run_prepare_ILP_IL run_prepare_ILP_NY run_prepare_ILP_TX run_prepare_ILP_CA

run_prepare_ILP_AL:
	python3 prepare_ILP.py AL_census  AL_do_redistrict AL_input_ILP
run_prepare_ILP_FL:
	python3 prepare_ILP.py FL_census  FL_do_redistrict FL_input_ILP
run_prepare_ILP_IL:
	python3 prepare_ILP.py IL_census  IL_do_redistrict IL_input_ILP
run_prepare_ILP_NY:
	python3 prepare_ILP.py NY_census  NY_do_redistrict NY_input_ILP
run_prepare_ILP_CA:
	python3 prepare_ILP.py CA_census  CA_do_redistrict CA_input_ILP
run_prepare_ILP_TX:
	python3 prepare_ILP.py TX_census  TX_do_redistrict TX_input_ILP

run_ILP_all: run_ILP_AL run_ILP_FL run_ILP_IL run_ILP_NY run_ILP_CA run_ILP_TX

run_ILP_AL:
	python3 reunification/ILP/split_pulp.py AL_input_ILP AL_output_ILP AL_log_ILP
run_ILP_FL:
	python3 reunification/ILP/split_pulp.py FL_input_ILP FL_output_ILP FL_log_ILP
run_ILP_IL:
	python3 reunification/ILP/split_pulp.py IL_input_ILP IL_output_ILP IL_log_ILP
run_ILP_NY:
	python3 reunification/ILP/split_pulp.py NY_input_ILP NY_output_ILP NY_log_ILP
run_ILP_CA:
	python3 reunification/ILP/split_pulp.py CA_input_ILP CA_output_ILP CA_log_ILP
run_ILP_TX:
	python3 reunification/ILP/split_pulp.py TX_input_ILP TX_output_ILP TX_log_ILP


generate_images_all: generate_images_AL generate_images_FL generate_images_IL generate_images_NY generate_images_CA generate_images_TX

generate_images_AL:
	python3 main_script.py AL AL_do_redistrict AL_census AL_output_ILP AL_gnuplot
	gnuplot	AL_gnuplot 
	gnuplot	AL_gnuplot_noreunification

generate_images_FL:
	python3 main_script.py FL FL_do_redistrict FL_census FL_output_ILP FL_gnuplot
	gnuplot	FL_gnuplot 
	gnuplot	FL_gnuplot_noreunification

generate_images_IL:
	python3 main_script.py IL IL_do_redistrict IL_census IL_output_ILP IL_gnuplot
	gnuplot	IL_gnuplot 
	gnuplot	IL_gnuplot_noreunification

generate_images_NY:
	python3 main_script.py NY NY_do_redistrict NY_census NY_output_ILP NY_gnuplot
	gnuplot	NY_gnuplot 
	gnuplot	NY_gnuplot_noreunification

generate_images_CA:
	python3 main_script.py CA CA_do_redistrict CA_census CA_output_ILP CA_gnuplot
	gnuplot	CA_gnuplot 
	gnuplot	CA_gnuplot_noreunification

generate_images_TX:
	python3 main_script.py TX TX_do_redistrict TX_census TX_output_ILP TX_gnuplot
	gnuplot	TX_gnuplot 
	gnuplot	TX_gnuplot_noreunification


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
