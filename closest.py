import census_block

def distsq(center3d, pt2d):
    #print("center3d", center3d)
    #print("pt2d", pt2d)
    x = center3d[0] - pt2d.x
    y = center3d[1] - pt2d.y
    return x*x + y*y + center3d[2]*center3d[2]

def generator(census_block_generator, C_3D):
    for block in census_block_generator:
        centroid = block.centroid
        j = min((i for i in range(len(C_3D))), key=lambda i:distsq(C_3D[i], centroid))
        yield block, j
        
'''

assignment_filename = "data/California_new_assignment.txt"
shape_filename = "data/California_census_blocks/tabblock2010_06_pophu"
output_filename = "data/census_block2district.txt"

f = open(assignment_filename)
line = f.readline()
k, n = [int(x) for x in line.split()]
centers = k*[None]
for i in range(k):
    centers[i] = tuple(float(x) for x in f.readline().split())

fout = open(output_filename, 'w')
for block in census_block.generator(shape_filename):
    if block.ID % 10000 == 0: print("block.ID ", block.ID)
    centroid = block.polygon.centroid
    block.centroid = centroid
    j = min((i for i in range(k)), key=lambda i:distsq(centers[i], centroid))
    fout.write(str(block.ID)+" "+str(j)+"\n")

fout.close()

'''
