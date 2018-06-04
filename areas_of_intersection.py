def gen(census_block_with_relevant_districts_generator, cells):
    for census_block, relevant_district_items in census_block_with_relevant_districts_generator:
        for relevant_district_item in relevant_district_items:
            relevant_district_item.area = census_block.polygon.intersection(cells[relevant_district_item.ID]).area
        yield census_block, relevant_district_items

