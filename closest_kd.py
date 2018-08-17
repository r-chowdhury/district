from scipy.spatial.kdtree import KDTree

def distsq(center3d, pt2d):
    x = center3d[0] - pt2d.x
    y = center3d[1] - pt2d.y
    return x * x + y * y + center3d[2] * center3d[2]


def gen(census_block_generator, C_3D):
    tree = KDTree(C_3D)
    blocks = list(census_block_generator)
    centroids = [(block.centroid.x,block.centroid.y,0)  for block in blocks]
    results = tree.query(centroids)
    return zip(blocks, results[1])

