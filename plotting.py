import matplotlib.pyplot as plt
from descartes import PolygonPatch


def find_bbox(pts):
    xmin, ymin, xmax, ymax = [f(g(pt) for pt in pts) for f in [min, max] for g in [(lambda pt:pt[0]), (lambda pt:pt[1])]]
    return (xmin, ymin), (xmax, ymax)

def plot_polygons(polygons):
    f, ax = plt.subplots()
    minpt, maxpt = find_bbox([pt for p in polygons for pt in p.exterior.coords])
    print("minpt ", minpt, " maxpt", maxpt)
    ax.set_xlim([minpt[0], maxpt[0]])
    ax.set_ylim([minpt[1], maxpt[1]])
    for polygon in polygons:
        ax.add_patch(PolygonPatch(polygon, facecolor='blue', edgecolor='black', alpha=.5))
    plt.show()


