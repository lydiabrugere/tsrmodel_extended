import numpy as np
import scipy
from scipy import ndimage
import math


class MetricsCalculation:

    def __init__(self, class_array, cell_size):
        self.class_array = class_array
        self.cell_size = cell_size
        self.cell_area_size = math.pow(cell_size,2)

    def f_structure_neighbor(self, class_array, s=2):
        """Label by Standard kernel"""
        self.class_array = class_array
        structure = scipy.ndimage.generate_binary_structure(s, s)
        labeled_array, num_patches = ndimage.label(class_array, structure)
        return labeled_array, num_patches

    def f_area(self, labeled_array):
        """Total area for a given class."""
        area = self.count_nonzero(labeled_array) * self.cellsize_2
        return area


    def f_landscape_area(self):
        """Total area for the landscape"""
        res = []
        for i in self.classes:
            arr = np.copy(self.array)
            arr[self.array != i] = 0
            res.append(self.f_returnArea(arr))
        return sum(res)


    def f_returnPatchPerimeter(self,labeled_array):
        """sum of patches perimeter"""
        labeled_array = self.f_setBorderZero(labeled_array) # make a border with zeroes
        total_perimeter = np.sum(labeled_array[:,1:] != labeled_array[:,:-1]) + np.sum(labeled_array[1:,:] != labeled_array[:-1,:])
        return total_perimeter


    def f_patch_density(self, num_patches):
        """Patch density"""
        total_area = self.f_landscape_area() # Calculate LArea
        try:
            val = (float(num_patches) / total_area)
        except ZeroDivisionError:
            val = None
        return val


    def f_return_patch(labeled_array,patch):
        """Return array with a specific labeled patch"""
        # Make an array of zeros the same shape as `a`.
        feature = np.zeros_like(labeled_array, dtype=int)
        feature[labeled_array == patch] = 1
        return feature


    def f_return_largest_patch_index(self,class_array,labeled_array,numpatches):
        """The largest patch index"""
        ma = self.f_returnPatchArea(class_array,labeled_array,numpatches,"max")
        self.f_landscape_area()
        return ( ma / self.Larea ) * 100