import util # for debugging

def generator(census_block_with_relevant_districts_generator, cells):
    for census_block, relevant_districts in census_block_with_relevant_districts_generator:
        if not all(i < len(cells) and i >= 0 for i in relevant_districts):
            print("areas of intersection", len(cells), relevant_districts, census_block.ID)
            fout = open("block", 'w')
            util.write_polygon(census_block.polygon)
            fout.close()
        areas = [census_block.polygon.intersection(cells[district]).area for district in relevant_districts]
        yield census_block, relevant_districts, areas

