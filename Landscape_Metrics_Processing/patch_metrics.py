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


def patch_area(array):
    """Return the area size for a given patch"""
    cell_size = 0.03
    cell_size_2 = math.pow(cell_size, 2)
    area_size = scipy.count_nonzero(array) * cell_size_2
    return area_size


def set_boarder_zero(array):
    """Returns the given matrix with a zero border coloumn and row around"""
    height, width = array.shape  # define height and width of input matrix
    array_boarder_zero = np.ones((height+(2*1), width+(2*1)))*0  # set the border to borderValue
    array_boarder_zero[1:height+1,1:width+1] = array  # set the interior region back to its original value
    return array_boarder_zero


def patch_perimeter(labeled_array):
    """Calculate the sum of patches perimeter"""
    array_boarder_zero = set_boarder_zero(array=labeled_array)  # make a border with zeroes
    total_perimeter = np.sum(array_boarder_zero[:, 1:] != array_boarder_zero[:,:-1]) + np.sum(array_boarder_zero[1:,:] != array_boarder_zero[:-1,:])
    return total_perimeter


def main():
    raster_path = "./data/se_mixed_forest_lu.tif"
    src_image = gdal.Open(str(raster_path))
    array = src_image.GetRasterBand(1).ReadAsArray()

    class_array = np.copy(array)
    classes = sorted(np.unique(array))  # a list of distinct classes
    class_array[class_array != classes[8]] = 0  # take class 'deciduous forest' (index 8, label 43) as an example
    s = ndimage.generate_binary_structure(2,2)
    labeled_array, num_patches = ndimage.label(class_array, s)
    labeled_array1, num_patches1 = ndimage.label(array, s)

    """Example to calculate patch area for each patch in deciduous forest class"""
    patch_area(class_array)

    """Example to calculate the class perimeter"""
    patch_perimeter(labeled_array) # 103835642  # TO DO: Check the calculation
