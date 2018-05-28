import shapefile
import sys

def get_census_block_shapes(infile, outfile):
    sf = shapefile.Reader(infile)
    of = open(outfile,'w')
    for shape_rec in sf.iterShapeRecords():
        pop = shape_rec.record[7]
        if pop > 0:
            for pt in shape_rec.shape.points:
                of.write(str(pt[0])+" "+str(pt[1])+" ")
            of.write("\n")
    of.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Use: ", sys.argv[0], "[input file (shape file)] [output file name]")
        exit(-1)
    get_census_block_shapes(sys.argv[1], sys.argv[2])

# /Users/klein/programming/district_data/California_census_block_data/tabblock2010_06_pophu
# California_nonzero_pop_census_blocks.dat
