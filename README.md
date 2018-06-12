Note that the file  code incorporates an adapted version of CS2, Andrew
Goldberg and Boris Cherkassky's implementation of a min-cost flow
algorithm due to Goldberg.  See cs2-COPYRIGHT for the license
information, and also see cs2-README.

The rest of the code is subject to the following license:
Copyright 2017 Philip N. Klein and Vincent Cohen-Addad

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Building the c++ code requires a compiler that can handle modern c++
features (for no good reason, I must admit).   Could use g++ version 7 or
clang++ version 4.  (Or could remove the structured binding.)

Before doing any US states, download cb_2016_us_state_500k.
(More details needed for this step.)

Extract census blocks and populations
  python3  census_block.py <census block shape filename> <output_filename>
where <census block shape filename> is name of shape file (not
  including suffix) specifying census blocks, e.g.
          tabblock010_44_pophu/tabblock2010_44_pophu
The directory can be downloaded as a zip file from https://www.census.gov/geo/maps-data/data/tiger-data.html
(Select Population & Housing Unit Counts -- Blocks, then select a state.)

The output file written has one line per client point.
It specifies the ID number of the corresponding census block, the x coordinate (longitude), the y coordinate
(latitude), and the population assigned to that point.
The script selects the point to be the centroid of the census block
shape.  If the census block consists of multiple polygons, the script
pretends each polygon is its own census block, and pretends the
population of each is zero.

Next, compute the clustering using
   do_redistrict <k> <input_filename>
where the first argument is the number of clusters to find, and the
input file is in the format of the output of the census_block.py script.
This program sends some text indicating progress to standard err, and,
when it terminates, sends the output to standard out.
 Output format:
    <num centers> <num clients>
    <center x> <center y> <center z>
    <center x> <center y> <center z>
    .
    .
    <center x> <center y> <center z>
    <census block ID> <client x> <client y> <center id> <subpopulation> <center id> <subpopulation> ... <center id> <subpopulation>
    <census block ID> <client x> <client y> <center id> <subpopulation> <center id> <subpopulation> ... <center id> <subpopulation>
    .
    .
    <census block ID> <client x> <client y> <center id> <subpopulation> <center id> <subpopulation> ... <center id> <subpopulation>

Standard out should be piped into a file

Next, compute a file for the ILP using
  python3 prepare_ILP.py <census block shape filename>  <redistricting solution filename  > <outputfilename>
where <census block shape filename> is as above, and <redistricting solution filename>
is the output from do_redistrict.

Next, run the ILP using
   python3 reunification/ILP/split_pulp.py <ILP input> <output filename> <log filename>
where <ILP input> is the result from prepare_ILP.py

Next, use
   python3 main_script.py <state abbreviation> <redistricting filename> <state shape filename> [<census block shape filename> <census block assignment filename>] <output filename>
   where
      <state abbreviation> is the two-capital-letter abbreviation for the state (e.g. CA or RI),
      <redistricting filename> is an output of the do_redistricting program,
      <state shape filename> is a file in the directory downloaded from the Census Bureau giving the census blocks and their populations,
      <census block assignment filename> is the output from the ILP solver, indicating how to assign census blocks to districts,
      and <output filename> is a gnuplot program. 
Square brackets [ ... ] indicate optional arguments.


Next, use
   gnuplot <filename> 
to produce a pdf file consisting of the redistricting of the region,
where <filename> is the name ofthe output file of main_script.
The pdf file's name is the same as <filename> but with .pdf at the end.




Other tools:

Function power_cells_fromfile(filename) takes
as input an output a file in the format of the output of 
do_redistrict and returns the list of polygons forming the cells of
the Voronoi diagram induced by the centers.

Similarly, Function power_cells(C_3D, bbox) takes a set
of centers and a bounding box and returns the list of polygons
forming the cells of the Voronoi diagram induced by C_3D that fits
into the bounding box bb

Function plot_helperVoronoi outputs a file that contains the clients
and their assignments and with the polygons output by power_cells.
Format of the file output is:
to produce a file that specifies:
   the client points, with colors reflecting the assignment to
   centers, and the boundaries of the convex polygons that form the
   power diagram of the chosen centers.
   
Format:
     <num centers> <num clients>
     <center x> <center y> <color>
     <center x> <center y> <color>
      .
      .
      <center x> <center y> <color>
      <x> <y> <x> <y> ... <x> <y> 
      <x> <y> <x> <y> ... <x> <y> 
      .
      .
      <x> <y> <x> <y> ... <x> <y> 



Function plot_helperGNUplot outputs a gnuplot script from
given the polygons, the bounding box, the shape of the state (used
to clip the polygons to the shape of the state) and displays the
clients (a.k.a. census blocks) or not depending on last argument.
Running gnuplot on that file shows the client points according
to the color assignment, and
also the state boundaries, and also the boundaries of the
power-diagram cells (clipped against the state boundaries).


Function plot_helperGNUplot_fromfile does the same thing than
the plot_helperGNUplot but takes as input a file in the format
of the file output by plot_helperVoronoi.
