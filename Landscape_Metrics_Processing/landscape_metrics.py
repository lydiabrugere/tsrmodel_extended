"""
This module calculate Area & Edge Metrics.
Index Options:
    1. Patch area (AREA): area (ha) of each patch.
    2. Patch radius of gyration (GYRATE)
    3. Class area (CA) or percentage of landscape (PLAND) – area (ha) of each patch type (class)
    4. Total edge (TE) or edge density (ED) – total length (m) or density (m/ha) of edge of a particular patch type (class level) or of all patch types (landscape level).
    5. Largest patch index (LPI) – percentage of the landscape comprised of the single largest patch (at the class or landscape level).

"""

import numpy as np
import math
import scipy
from scipy import ndimage
from osgeo import gdal


def area(array):
    """Return the total area for the given class"""
    cell_size = 0.03
    cellsize_2 = math.pow(cell_size, 2)
    area_size = scipy.count_nonzero(array) * cellsize_2
    return area_size


def landscape_area(array):
    """Aggregates all class area, equals the sum of total area for each class"""
    res = []
    classes = sorted(np.unique(array))
    for i in classes:
        class_array = np.copy(array)
        class_array[class_array != i] = 0
        res.append(area(class_array))
    return sum(res)


def main():
    raster_path = "./data/se_mixed_forest_lu.tif"
    src_image = gdal.Open(str(raster_path))
    array = src_image.GetRasterBand(1).ReadAsArray()

    # this calculate the landscape area
    landscape_area(array)

    class_array = np.copy(array)
    class_array[class_array != 43] = 0

    s = ndimage.generate_binary_structure(2,1)
    labeled_array, numpatches = ndimage.label(class_array, s)

