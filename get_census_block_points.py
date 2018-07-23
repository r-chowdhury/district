import census_block_file

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Use python3 ",
            sys.argv[0],
            "<path to shape file containing census blocks (without suffix)> <output filename>",
        )
        exit(-1)
    binary_census_block_data_filename = sys.argv[1]
    output_filename = sys.argv[2]
    of = open(output_filename, "w")
    for census_block in census_block_file.read(binary_census_block_data_filename):
        if census_block.ID % 10000 == 0:
            print(census_block.ID)
        centroid = census_block.polygon.centroid
        pop = census_block.population
        if pop > 0:
            of.write(
                str(census_block.ID)
                + " "
                + str(centroid.x)
                + " "
                + str(centroid.y)
                + " "
                + str(pop)
                + "\n"
            )
    of.close()
