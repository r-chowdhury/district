from census_block import Census_Block

def gen(census_block_plus_district_items_collection, cells, starting_number):
    counter = starting_number
    for block, district_items in census_block_plus_district_items_collection:
        if len(district_items) > 1 and block.population == 0:
            for district_item in district_items:
                geom = block.polygon.intersection(cells[district_item.ID])
                objects = [geom] if geom.geom_type == 'Polygon' else geom
                for object in objects:
                    if object.geom_type == 'Polygon':
                        b = Census_Block(counter, object, 0)
                        counter += 1
                        yield b, [district_item]
        else:
            yield block, district_items
