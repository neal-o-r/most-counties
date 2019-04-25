import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader
from shapely.geometry import Polygon, Point
from descartes import PolygonPatch
import numpy as np
import rasterio

src = rasterio.open("counties/srtm_35_02.tif")
band = src.read(1)

fname = "counties/counties.shp"
bounds = [-10.75,-5.2,51.2,55.5]
carrauntoohil = (51.999445, -9.742693)
burtonhall = (52.859912, -6.862953)


def elevation(pt):
    vals = src.index(pt[1], pt[0])
    if vals[0] >= band.shape[0] or vals[1] >= band.shape[0]:
        return 2
    h = band[vals]
    return h if h > 0 else 2


def read_shps(fname):
    return shapereader.Reader(fname)


def make_circle(x, y):
    km1 = 1 / 110.5
    size = 3.57 * np.sqrt(elevation((y, x)))
    return Point(x, y).buffer(size * km1)


def point_overlaps(x, y, counties):
    p = make_circle(x, y)
    return [c.intersection(p).area > 0.05 for c in counties]


def make_grid(bounds):
    lat = np.linspace(bounds[0], bounds[1], 50)
    lng = np.linspace(bounds[2], bounds[3], 50)
    return lat, lng


def counties_overlap(x, y, counties, shps):
    overs = point_overlaps(x, y, counties)
    return [rec.attributes['NAME_TAG'] for rec, o in
            zip(list(shps.records()), overs) if o]


def plot_map(counties, poly=None):

    fig1 = plt.figure(figsize=(10,10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(bounds)
    ax.gridlines()

    ax.add_geometries(counties, ccrs.PlateCarree(),
                edgecolor='black', facecolor='gray', alpha=0.5)

    if poly is not None:
        for p in poly:
            ax.add_patch(PolygonPatch(p,  fc='r', ec='#555555',
                alpha=0.5, zorder=5))

    plt.show()

if __name__ == "__main__":
    shps = read_shps("counties/counties.shp")
    counties = list(shps.geometries())

    latitudes, longitudes = make_grid(bounds)

    n_overlaps = np.zeros((len(latitudes), len(longitudes)))
    for i, lat in enumerate(latitudes):
        print(i)
        for j, lng in enumerate(longitudes):
            overlaps = point_overlaps(lat, lng, counties)
            n_overlaps[i][j] = sum(overlaps)

    all_inds = np.argwhere(n_overlaps == np.amax(n_overlaps))
    np.save("50x50_overlaps.npy", n_overlaps)
