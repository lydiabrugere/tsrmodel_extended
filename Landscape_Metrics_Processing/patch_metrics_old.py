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
    """Return the total area for a given patch"""
    cell_size = 0.03
    cell_size_2 = math.pow(cell_size, 2)
    area_size = scipy.count_nonzero(array) * cell_size_2
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


def patch_density(num_patches, array):
    """Calculate Patch density"""
    ls_area = landscape_area(array)  # Calculate ls_area
    try:
        patch_den = (float(num_patches) / float(ls_area))
    except ZeroDivisionError:
        patch_den = None
    return patch_den


def patch_area(class_array, labeled_array, num_patches, stat):
    """Calculate greatest, smallest or mean patch area for a class"""
    cell_size = 0.03
    cell_size_2 = math.pow(cell_size, 2)
    # calculate the value sum of each labeled patch
    sizes = ndimage.sum(input=class_array, labels=labeled_array, index=range(1, num_patches + 1))
    sizes = sizes[sizes != 0]  # remove zeros
    if len(sizes) != 0:
        if stat == "max":
            return np.max(sizes) * cell_size_2
        elif stat == "min":
            return np.min(sizes) * cell_size_2
        elif stat == "mean":
            return np.mean(sizes) * cell_size_2
        elif stat == "median":
            return np.median(sizes) * cell_size_2
    else:
        return None


def largest_patch_index(class_array, labeled_array, num_patches):
    """The largest patch index: LPI equals the percentage of the landscape comprised by the largest patch"""
    max_area = patch_area(class_array, labeled_array, num_patches, "max")
    Larea = landscape_area(class_array)
    return (max_area/Larea) * 100  # convert to percentage


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


def core_area(labeled_array):
    """Calculate the overall Core Area: after removing edge effects"""
    cell_size = 0.03
    cell_size_2 = math.pow(cell_size, 2)
    s = ndimage.generate_binary_structure(2,2)
    newlab = ndimage.binary_erosion(labeled_array, s).astype(labeled_array.dtype)
    return ndimage.sum(newlab) * cell_size_2


def labeled_patch(labeled_array,patch):
    """Return array with a specific labeled patch"""
    labeled_patch = np.zeros_like(labeled_array, dtype=int)
    labeled_patch[labeled_array == patch] = 1
    return labeled_patch


def internal_edge(class_array):
    """Internal edge: Count of neighboring non-zero cell"""
    kernel = ndimage.generate_binary_structure(2, 1)
    kernel[1, 1] = 0
    b = ndimage.convolve(class_array, kernel, mode="constant")
    n_interior = b[class_array != 0].sum()   # Number of interiror edges
    return n_interior


def get_prop_adjacency(labeled_array, num_patches):
    """Calculate adjacenies"""
    internalEdges = np.array([]).astype(float)
    outerEdges = np.array([]).astype(float)
    for i in range(1, num_patches + 1):  # Very slow!
        feature = labeled_patch(labeled_array, i)
        outerEdges = np.append(outerEdges, float(patch_perimeter(labeled_patch)))
        internalEdges = np.append(internalEdges, float(internal_edge(feature)))

    prop = np.sum(internalEdges) / np.sum(internalEdges + outerEdges * 2)
    return prop


def main():
    raster_path = "./data/se_mixed_forest_lu.tif"
    src_image = gdal.Open(str(raster_path))
    array = src_image.GetRasterBand(1).ReadAsArray()

    class_array = np.copy(array)
    classes = sorted(np.unique(array))  # a list of distinct classes
    class_array[class_array != classes[8]] = 0  # take class 'deciduous forest' (index 8, label 43) as an example
    s = ndimage.generate_binary_structure(2,1)
    labeled_array, num_patches = ndimage.label(class_array, s)

    """Example to calculate patch density for deciduous forest"""
    patch_density(num_patches, array)  # Result for mixed_forest: 3.765447293431706

    """Example to calculate the largest patch index for deciduous forest class"""
    largest_patch_index(class_array, labeled_array, num_patches)

    """Example to calculate the smallest patch area for deciduous forest class"""
    stat = "min"
    patch_area(class_array, labeled_array, num_patches, stat)  # 0.0387

    """Example to calculate the largest patch area for deciduous forest class"""
    stat = "max"
    patch_area(class_array, labeled_array, num_patches, stat)  # 2371

    """Example to calculate the class perimeter"""
    patch_perimeter(labeled_array) # 103835642  # TO DO: Check the calculation

    """Example to calcualte core area"""
    core_area(labeled_array)