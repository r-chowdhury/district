import census_block_file
import sys

if __name__ == '__main__':
    #argument 1: name of binary file storing blocks
    #argument 2: name of text file specifying assignment to some blocks
    #argument 3: name of file in which to store binary data on blocks assigned
    assignment = {int(s[0]):int(s[1]) for s in (line.split() for line in open(sys.argv[2]))}
    block_out = open(sys.argv[3],"wb")
    for block in census_block_file.read(sys.argv[1]):
        if block.ID in assignment:
            block.home_district = assignment[block.ID]
            census_block_file.write(block_out, block)
