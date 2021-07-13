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

from scipy import ndimage
from osgeo import gdal

rasterPath = "./data/se_mixed_forest_lu.tif"
srcImage = gdal.Open(str(rasterPath))
array = srcImage.GetRasterBand(1).ReadAsArray()
class_array = np.copy(array)
class_array[class_array != 43] = 0

s = ndimage.generate_binary_structure(2,1)
labeled_array, numpatches = ndimage.label(class_array, s)

"""
Considering immediate and diagonal neighbors as a patch
    [[1,1,1],
    [1,1,1],
    [1,1,1]]

"""


def patch_area(class_array, target_class, cell_size, stat):
    """Calculate greatest, smallest, mean or median patch area"""
    s = ndimage.generate_binary_structure(2, 2)
    labeled_array, num_patch = ndimage.label(class_array, s)
    cell_size_2 = math.pow(cell_size, 2)
    sizes = ndimage.sum(class_array, labeled_array, range(1, num_patch + 1))
    sizes = sizes[sizes != 0]
    if len(sizes) != 0:
        if stat == "max":
            return (np.max(sizes) * cell_size_2) / int(target_class)
        elif stat == "min":
            return (np.min(sizes) * cell_size_2) / int(target_class)
        elif stat == "mean":
            return (np.mean(sizes) * cell_size_2) / int(target_class)
        elif stat == "median":
            return (np.median(sizes) * cell_size_2) / int(target_class)
    else:
        return None

def patch_perimeter(class_array, target_class):

    """Calculate patch perimeter"""
    heightFP, widthFP = class_array.shape  # define hight and width of input matrix
    withBorders = np.ones((heightFP + (2 * 1), widthFP + (2 * 1))) * 0  # set the border to borderValue
    withBorders[1:heightFP + 1, 1:widthFP + 1] = class_array  # set the interior region to the input matrix

def class_area(array, target_class, cell_size):
    """Total area for a given class"""
    class_array = np.copy(array)
    class_array[class_array != target_class] = 0

    patch = patch_area(cell_size)
    area = np.count_nonzero(class_array) * patch
    return area


