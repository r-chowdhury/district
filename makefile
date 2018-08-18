# makefile for cs2
# compileler definitions
# COMP_DUALS to compute prices
# PRINT_ANS to print flow (and prices if COMP_DUAL defined)
# COST_RESTART to be able to restart after a cost function change
# NO_ZERO_CYCLES finds an opeimal flow with no zero-cost cycles
# CHECK_SOLUTION check feasibility/optimality. HIGH OVERHEAD!

# change these to suit your system
CCOMP = g++ #clang++
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

# STATES = AL CA FL IL NY TX RI
# RI is just for testing

STATES = AL AZ AR CA CO CT FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO NE NV NH NJ NM NY NC OH OK OR PA RI SC TN TX UT VA WA WV WI
#states with single congressional districts: AK, DE, MT, ND, SD, VT, WY
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

AL_POPID = 01# Alabama
AK_POPID = 02# Alaska
AZ_POPID = 04# Arizona
AR_POPID = 05# Arkansas
CA_POPID = 06# California
CO_POPID = 08# Colorado
CT_POPID = 09# Connecticut
DE_POPID = 10# Delaware
# DC_POPID = 11# District of Columbia
FL_POPID = 12# Florida
GA_POPID = 13# Georgia
HI_POPID = 15# Hawaii
ID_POPID = 16# Idaho
IL_POPID = 17# Illinois
IN_POPID = 18# Indiana
IA_POPID = 19# Iowa
KS_POPID = 20# Kansas
KY_POPID = 21# Kentucky
LA_POPID = 22# Louisiana
ME_POPID = 23# Maine
MD_POPID = 24# Maryland
MA_POPID = 25# Massachusetts
MI_POPID = 26# Michigan
MN_POPID = 27# Minnesota
MS_POPID = 28# Mississippi
MO_POPID = 29# Missouri
MT_POPID = 30# Montana
NE_POPID = 31# Nebraska
NV_POPID = 32# Nevada
NH_POPID = 33# New Hampshire
NJ_POPID = 34# New Jersey
NM_POPID = 35# New Mexico
NY_POPID = 36# New York
NC_POPID = 37# North Carolina
ND_POPID = 38# North Dakota
OH_POPID = 39# Ohio
OK_POPID = 40# Oklahoma
OR_POPID = 41# Oregon
PA_POPID = 42# Pennsylvania
RI_POPID = 44# Rhode Island
SC_POPID = 45# South Carolina
SD_POPID = 46# South Dakota
TN_POPID = 47# Tennessee
TX_POPID = 48# Texas
UT_POPID = 49# Utah
VT_POPID = 50# Vermont
VA_POPID = 51# Virginia
WA_POPID = 53# Washington
WV_POPID = 54# West Virginia
WI_POPID = 55# Wisconsin
WY_POPID = 56# Wyoming

# AL_POPID = 01
# CA_POPID = 06
# FL_POPID = 12
# IL_POPID = 17
# NY_POPID = 36
# TX_POPID = 48

# RI_POPID = 44

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
################# 2. preprocess_census_block.py  
#################

$(STATES:%=$(OUT)/preprocess_census_block/%): $(OUT)/preprocess_census_block/%: data/%_census_blocks preprocess_census_block.py census_block_file.py
	@ mkdir -p $(OUT)/preprocess_census_block
	python3 preprocess_census_block.py data/$*_census_blocks/tabblock2010_$($*_POPID)_pophu $@
	@ test -s $@

# .PRECIOUS: $(OUT)/census_block/%

#################
################# 2.5 get_census_block_points.py  
#################

$(STATES:%=$(OUT)/get_census_block_points/%): $(OUT)/get_census_block_points/%: $(OUT)/preprocess_census_block/% get_census_block_points.py census_block_file.py
	@ mkdir -p $(OUT)/get_census_block_points
	python3 get_census_block_points.py $< $@
	@ test -s $@

# .PRECIOUS: $(OUT)/census_block/%

#################
################# 3. do_redistrict
#################

# AL_DISTRICTS = 7
# CA_DISTRICTS = 53
# FL_DISTRICTS = 27
# IL_DISTRICTS = 18
# NY_DISTRICTS = 27
# TX_DISTRICTS = 36

# from https://en.wikipedia.org/wiki/United_States_congressional_apportionment#Past_apportionments

AK_DISTRICTS = 1
AL_DISTRICTS = 7
AR_DISTRICTS = 4
AZ_DISTRICTS = 9
CA_DISTRICTS = 53
CO_DISTRICTS = 7
CT_DISTRICTS = 5
DE_DISTRICTS = 1
FL_DISTRICTS = 27
GA_DISTRICTS = 14
HI_DISTRICTS = 2
IA_DISTRICTS = 4
ID_DISTRICTS = 2
IL_DISTRICTS = 18
IN_DISTRICTS = 9
KS_DISTRICTS = 4
KY_DISTRICTS = 6
LA_DISTRICTS = 6
MA_DISTRICTS = 9
MD_DISTRICTS = 8
ME_DISTRICTS = 2
MI_DISTRICTS = 14
MN_DISTRICTS = 8
MO_DISTRICTS = 8
MS_DISTRICTS = 4
MT_DISTRICTS = 1
NC_DISTRICTS = 13
ND_DISTRICTS = 1
NE_DISTRICTS = 3
NH_DISTRICTS = 2
NJ_DISTRICTS = 12
NM_DISTRICTS = 3
NV_DISTRICTS = 4
NY_DISTRICTS = 27
OH_DISTRICTS = 16
OK_DISTRICTS = 5
OR_DISTRICTS = 5
PA_DISTRICTS = 18
RI_DISTRICTS = 2
SC_DISTRICTS = 7
SD_DISTRICTS = 1
TN_DISTRICTS = 9
TX_DISTRICTS = 36
UT_DISTRICTS = 4
VA_DISTRICTS = 11
VT_DISTRICTS = 1
WA_DISTRICTS = 10
WI_DISTRICTS = 8
WV_DISTRICTS = 3
WY_DISTRICTS = 1


$(STATES:%=$(OUT)/do_redistrict/%): $(OUT)/do_redistrict/%: $(OUT)/get_census_block_points/% do_redistrict
	@ mkdir -p $(OUT)/do_redistrict
	./do_redistrict $($*_DISTRICTS) $< > $@
	@ test -s $@

# .PRECIOUS: $(OUT)/do_redistrict/%

#################
################# 3. prepare_ILP.py
#################
#example: python3 prepare_ILP.py FL shapestate_data/cb_2017_us_state_500k makefile_outputs/preprocess_census_block/FL makefile_outputs/do_redistrict/FL makefile_outputs/prepare_ILP/FL

$(OUT)/prepare_ILP/% $(OUT)/prepare_ILP/%_blockdata: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* $(OUT)/preprocess_census_block/% prepare_ILP.py
	@ mkdir -p $(OUT)/prepare_ILP
	python3 prepare_ILP.py $* shapestate_data/cb_2017_us_state_500k $(OUT)/preprocess_census_block/$* $< $@ $@_blockdata
	@ test -s $@

# .PRECIOUS: $(OUT)/prepare_ILP/%

#################
################# 4. split_pulp -- solve ILP
#################
#example: python3 reunification/ILP/split_pulp.py gurobi makefile_outputs/prepare_ILP/RI makefile_outputs/split_pulp/RI makefile_outputs/split_pulp/RI.log
SPLIT_PULP = reunification/ILP/split_pulp.py
SOLVER = gurobi

$(STATES:%=$(OUT)/split_pulp/%): $(OUT)/split_pulp/%: $(OUT)/prepare_ILP/% $(SPLIT_PULP)
	@ mkdir -p $(OUT)/split_pulp
	python3 $(SPLIT_PULP) $(SOLVER) $< $@ $@.log
	@ test -s $@

# .PRECIOUS: $(OUT)/split_pulp/%

#################
################# 4.5. verify
#################

$(STATES:%=$(OUT)/verify/%): $(OUT)/verify/%: $(OUT)/split_pulp/% $(OUT)/prepare_ILP/%_blockdata $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* verify.py
	@ mkdir -p $(OUT)/verify
	python3 verify.py $* shapestate_data/cb_2017_us_state_500k $(OUT)/prepare_ILP/$*_blockdata $(OUT)/do_redistrict/$* $(OUT)/split_pulp/$* $(OUT)/verify/$*.log
	touch $(OUT)/verify/$*

#################
################# 5. main_script
#################

## main_script with reunification

$(STATES:%=$(OUT)/main_script/%_blocks): $(OUT)/main_script/%_blocks: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* $(OUT)/split_pulp/% $(OUT)/prepare_ILP/%_blockdata main_script.py main_plot.py
	@ mkdir -p $(OUT)/main_script
	python3 main_script.py $* $(OUT)/do_redistrict/$* shapestate_data/cb_2017_us_state_500k $(OUT)/preprocess_census_block/$* $(OUT)/split_pulp/$* $@
	@ test -s $@

# .PRECIOUS: $(OUT)/main_script/%_blocks

## main_script without reunification

$(STATES:%=$(OUT)/main_script/%_districts): $(OUT)/main_script/%_districts: $(OUT)/do_redistrict/% shapestate_data/cb_2017_us_state_500k* $(OUT)/split_pulp/% main_script.py
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
