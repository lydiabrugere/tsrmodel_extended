import argparse
import pandas as pd
import numpy as np
import math
import scipy
from scipy import ndimage
import rasterio
from scipy import stats


def total_class_area(class_array):
    """Return the total area for the given class"""
    cell_size = 0.03
    cellsize_2 = math.pow(cell_size, 2)
    CA = scipy.count_nonzero(class_array) * cellsize_2
    return CA


def number_of_patches(class_array):
    s = ndimage.generate_binary_structure(2, 1)
    _, NP = ndimage.label(class_array, s)
    return NP


def label_patch(class_array):
    """Lable patches for a given class"""
    struct = scipy.ndimage.generate_binary_structure(2, 1)
    labeled_array, num_patches = ndimage.label(class_array, struct)
    return labeled_array, num_patches


def patch_density(array, classes, class_array):
    """Calculate Patch density"""
    for class_type in classes:
        cl_array = np.copy(array)
        cl_array[cl_array != int(class_type)] = 0
        ca = total_class_area(class_array=cl_array)  # Calculate ls_area
        ca += ca
    try:
        NP= number_of_patches(class_array)
        PD = (float(NP) / float(ca))
    except ZeroDivisionError:
        PD = None
    return PD


def set_border_zero(array):
    """Add a zero border column and row around matrix"""
    num_row, num_col = array.shape  # define hight and width of input matrix
    with_borders = np.ones((num_row+(2*1), num_col+(2*1)))*0 # set the border to borderValue
    with_borders[1:num_row+1, 1:num_col+1] = array  # set the interior region to the input matrix
    return with_borders


def total_edge(labeled_array):
    """Calculate sum of patches perimeter"""
    with_borders = set_border_zero(labeled_array)  # make a border with zeroes
    edge_count = np.sum(with_borders[:, 1:] != with_borders[:, :-1]) + np.sum(with_borders[1:, :] != with_borders[:-1, :])
    cell_size = 0.03
    TE = edge_count * cell_size
    return TE


def edge_density(labeled_array, total_area):
    """Calculate edge Density"""
    try:
        ED = float(total_edge(labeled_array)) / float(total_area)
    except ZeroDivisionError:
        ED = None
    return ED


def total_area(class_array, labeled_array, num_patches, stat):
    """Calculate greatest, smallest or mean patch area for a class"""
    cell_size = 0.03
    cell_size_2 = math.pow(cell_size, 2)
    # calculate the sum of value of the class array; Assign labels to the values of the array; labeled_array
    sizes = ndimage.sum(input=class_array, labels=labeled_array, index=range(1, num_patches+1))
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
        elif stat == "std":
            return np.std(sizes) * cell_size_2
    else:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Diversity Indexes')
    parser.add_argument('--raster_path', required=True, help='This is the image path on the OS system')
    parser.add_argument('--class_metrics_code', required=True, help='What class matrix to calculate? refer to metrics codes?')

    args = parser.parse_args()
    raster_path = args.raster_path
    class_metrics_code = args.class_metrics_code

    src = rasterio.open(raster_path)
    array = src.read(1)
    cl_array = np.copy(array)
    classes = sorted(np.unique(cl_array))  # a list of distinct classes
    NoData = src.nodatavals
    classes.remove(NoData)

    # C3: Total (Class) Area (CA)
    if class_metrics_code == "C3":
        df = pd.DataFrame(columns=['class_type', 'C3_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            c3_value = total_class_area(class_array=cl_array)
            df=df.append({'class_type':class_type, 'C3_value':c3_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C3_output.csv")

    # TODO: C4: Percentage of Landscape (PLAND)

    # C5: Number of Patches(NP)
    elif class_metrics_code == "C5":
        df = pd.DataFrame(columns=['class_type', 'C5_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            c5_value = number_of_patches(class_array=cl_array)
            df = df.append({'class_type': class_type, 'C5_value': c5_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C5_output.csv")

    # C6: Patch Density (PD)
    elif class_metrics_code == "C6":
        df = pd.DataFrame(columns=['class_type', 'C6_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            c6_value = patch_density(array=array, classes=classes, class_array=cl_array)
            df = df.append({'class_type': class_type, 'C6_value': c6_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C6_output.csv")

    # C7: Total Edge (TE)
    elif class_metrics_code == "C7":
        df = pd.DataFrame(columns=['class_type', 'C7_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            c7_value = total_edge(labeled_array=cl_array)
            df = df.append({'class_type': class_type, 'C7_value': c7_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C7_output.csv")

    # C8: Edge Density (ED)
    elif class_metrics_code == "C8":
        df = pd.DataFrame(columns=['class_type', 'C8_value'])
        res = []
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            res.append(total_class_area(cl_array))
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != class_type] = 0
            c8_value = edge_density(labeled_array=cl_array, total_area=sum(res))
            df = df.append({'class_type': class_type, 'C8_value': c8_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C8_output.csv")

    # TODO: C9: Landscape Shape Index (LSI): figure out the denominator: minimum length or area?
    elif class_metrics_code == "C9":
        for class_type in classes:
            cl_array[array != int(class_type)] = 0
            c7_value = total_edge(labeled_array=cl_array)

    # C10: Largest Patch Index (LPI)
    elif class_metrics_code == "C10":
        df = pd.DataFrame(columns=['class_type', 'C10_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            s = ndimage.generate_binary_structure(2, 1)
            labeled_array, num_patches = ndimage.label(cl_array, s)
            c10_value = total_area(class_array=cl_array, labeled_array=labeled_array, num_patches=num_patches, stat='max')
            df = df.append({'class_type': class_type, 'C10_value': c10_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C10_output.csv")

    # Patch Area Distribution: mean (AREA_MN)
    elif class_metrics_code == "C11":
        df = pd.DataFrame(columns=['class_type', 'C11_value'])
        cell_size = 0.03
        cell_size_2 = math.pow(cell_size, 2)
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)
            sizes = ndimage.sum(input=cl_array, labels=labeled_array, index=range(1, num_patches + 1))
            sizes = sizes[sizes != 0]  # remove zeros
            try:
                c11_value = np.sum(sizes) * cell_size_2 / number_of_patches(class_array=cl_array)
            except ZeroDivisionError:
                c11_value = None
            df = df.append({'class_type': class_type, 'C11_value': c11_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C11_output.csv")

    # Patch Area Distribution: area-weighted mean (AREA_AM)
    elif class_metrics_code == "C11":
        df = pd.DataFrame(columns=['class_type', 'C12_value'])
        cell_size = 0.03
        cell_size_2 = math.pow(cell_size, 2)
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)
            sizes = ndimage.sum(input=cl_array, labels=labeled_array, index=range(1, num_patches+1))
            sizes = sizes[sizes != 0]  # remove zeros
            prop = sizes/np.sum(sizes)
            c12_value = np.sum(sizes) * cell_size_2 * prop
            df = df.append({'class_type': class_type, 'C12_value': c12_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C12_output.csv")

    # Patch Area Distribution: Median (MD)
    elif class_metrics_code == "C13":
        df = pd.DataFrame(columns=['class_type', 'C13_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)
            c13_value = total_area(cl_array, labeled_array, num_patches, stat='median')
            df = df.append({'class_type': class_type, 'C13_value': c13_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C13_output.csv")

    # Patch Area Distribution: Range (RA)
    elif class_metrics_code == "C14":
        df = pd.DataFrame(columns=['class_type', 'C14_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)
            max = total_area(cl_array, labeled_array, num_patches, stat='max')
            min = total_area(cl_array, labeled_array, num_patches, stat='min')
            C14_value = max - min
            df = df.append({'class_type': class_type, 'C14_value': C14_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C14_output.csv")

    # Patch Area Distribution: Standard deviation (std)
    elif class_metrics_code == "C15":
        df = pd.DataFrame(columns=['class_type', 'C15_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)
            C15_value = total_area(cl_array, labeled_array, num_patches, stat='std')
            df = df.append({'class_type': class_type, 'C15_value': C15_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C15_output.csv")

    # Patch Area Distribution: Coefficient of variation (CV)
    elif class_metrics_code == "C16":
        df = pd.DataFrame(columns=['class_type', 'C16_value'])
        cell_size = 0.03
        cell_size_2 = math.pow(cell_size, 2)
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)
            SD = total_area(cl_array, labeled_array, num_patches, stat='std')
            sizes = ndimage.sum(input=cl_array, labels=labeled_array, index=range(1, num_patches + 1))
            sizes = sizes[sizes != 0]
            try:
                MN = np.sum(sizes) * cell_size_2 / number_of_patches(class_array=cl_array)
            except ZeroDivisionError:
                MN = None
            C16_value = SD/MN * 100
            df = df.append({'class_type': class_type, 'C16_value': C16_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C16_output.csv")

    # (C23) Perimeter-Area Fractal Dimension
    elif class_metrics_code == "C23":
        df = pd.DataFrame(columns=['class_type', 'C23_value'])
        for class_type in classes:
            cl_array = np.copy(array)
            cl_array[array != int(class_type)] = 0
            labeled_array, num_patches = label_patch(class_array=cl_array)

            # calculate each patch area
            area = ndimage.sum(input=cl_array, labels=labeled_array, index=range(1, num_patches + 1))
            cell_size = 0.03
            cell_size_2 = math.pow(cell_size, 2)
            area = area[area != 0] * cell_size_2

            # calculate each patch perimeter
            kernel = ndimage.generate_binary_structure(2, 1)  # Make a kernel
            kernel[1, 1] = 0
            cl_array = np.copy(array)
            b = ndimage.convolve(cl_array, kernel, mode="constant")
            perim = ndimage.sum(input=b, labels=labeled_array, index=range(1, num_patches + 1))
            slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(perim), np.log(area))

            C23_value = 2/slope
            df = df.append({'class_type': class_type, 'C23_value': C23_value}, ignore_index=True)
        df.to_csv("./ouput/class_metrics/C23_value.csv")

    # C24-C29 Perimeter-Area Ratio Distribution (PARA_MN, _AM, _MD, _RA, _SD, _CV)