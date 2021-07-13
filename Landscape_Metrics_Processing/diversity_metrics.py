"""
This module calculate species diversity metrics from satellite imagery.
Index Options:
    1. Richness:
        1.1 Patch richness (PR) : number of patch type present
            Example run:
        `python diversity_calc_function.py --raster_path "./data/se_mixed_forest_lu.tif" --index_category "richness" --index "patch_richness"`
        1.2 Patch richness density (PRD): richness per area (ha)
            Example run:
        `python diversity_calc_function.py --raster_path "./data/se_mixed_forest_lu.tif" --index_category "richness" --index "patch_richness_density" --cell_size 0.03`
        1.3 Relative patch richness (RPR): PR divided by maximum potential PR as specified by the user
            Example run:
        `python diversity_calc_function.py --raster_path "./data/se_mixed_forest_lu.tif" --index_category "richness" --index "relative_patch_richness" --max_potential_richness 20`
    2. Evenness:
        2.1 Simpson: the probability that any two cells selected at random would be different patch types
            Example run:
        `./venv/bin/python3 diversity_calc_function.py --raster_path "./data/se_mixed_forest_lu.tif" --index_category evenness --index "simpson"`
        Shannon:
            Example run:
        `./venv/bin/python3 diversity_calc_function.py --raster_path "./data/se_mixed_forest_lu.tif" --index_category evenness --index "shannon"`
Todo:
    * Add error handling and pipe output to save

"""

import numpy as np
import math
import argparse
from osgeo import gdal


def f_richness_index(array, index, no_data, cell_size=None, max_potential_pr=None):

    classes = sorted(np.unique(array))
    classes.remove(no_data)
    array[array == int(no_data)] = 0
    if cell_size:
        area = np.count_nonzero(array) * cell_size

    if index == "patch_richness":
        patch_richness_index = len(classes)
        print("Patch Richness: ", patch_richness_index)
        return patch_richness_index

    elif index == "patch_richness_density":
        patch_richness_density_index = len(classes)/area
        print("Patch Richness Density: ", patch_richness_density_index)
        return patch_richness_density_index

    elif index == "relative_patch_richness":
        relative_patch_richness_index = len(classes)/float(max_potential_pr)
        print("Relative Patch Richness: ", relative_patch_richness_index)
        return relative_patch_richness_index
    else:
        print("Invalid diversity index of choice. Only accept 'patch_richness', 'patch_richness_density' and 'relative_patch_richness'")


def f_evenness_index(array, index, no_data):

    classes = sorted(np.unique(array))
    classes.remove(no_data)

    """total count of NON-nodata value e.g.: 556110932"""
    array2 = np.copy(array)
    array2[array2 == int(no_data)] = 0
    total_classes_count = np.count_nonzero(array2)

    target_class_count_list = []
    for target_class in classes:
        array1 = np.copy(array)
        array1[array1 != target_class] = 0  # all non-target class as 0
        target_class_count = np.count_nonzero(array1)
        target_class_count_list.append(target_class_count)

    pro = [ele/total_classes_count for ele in target_class_count_list]

    if index == "simpson":
        simpson_index =[math.pow(ele, 2) for ele in pro]
        simpson_diversity_index = 1 - sum(simpson_index)
        print("Simpson Diversity Index: ", simpson_diversity_index)
        return simpson_diversity_index

    elif index == "shannon":
        shannon_index = [ele * math.log(ele) for ele in pro]
        shannon_diversity_index = sum(shannon_index) * -1
        print("Shannon Diversity Index: ", shannon_diversity_index)
        return shannon_diversity_index

    else:
        print("Invalid diversity index of choice. Only accept 'simpson' or 'shannon!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate Diversity Indexes')
    parser.add_argument('--raster_path', required=True, help='This is the image path on the OS system')
    parser.add_argument('--index_category', required=True, help='What type of index to calculate? richness or evenness?')
    parser.add_argument('--index', required=True, help='Which diversity index to calculate? shannon, simpson, patch_richness, patch_richness_density,'
                                                       ' relative_patch_richness?')
    parser.add_argument('--cell_size', required=False, help='What is the cell width/height of one pixel in the image?')
    parser.add_argument('--max_potential_richness', required=False, help='What is the max potential richness in this landscape?')

    args = parser.parse_args()
    raster_path = args.raster_path
    index_category = args.index_category
    diversity_index = args.index

    raster = gdal.Open(raster_path)
    band = raster.GetRasterBand(1)
    image_array = band.ReadAsArray()
    NoData = band.GetNoDataValue()

    if index_category == "richness":
        if args.cell_size:
            CellSize = float(args.cell_size) ** 2
            f_richness_index(array=image_array, index=diversity_index, no_data=NoData, cell_size=CellSize)
        elif args.max_potential_richness:
            max_potential_richness = args.max_potential_richness
            f_richness_index(array=image_array, index=diversity_index, no_data=NoData, max_potential_pr=max_potential_richness)
        else:
            f_richness_index(array=image_array, index=diversity_index, no_data=NoData)

    elif index_category == "evenness":
        f_evenness_index(array=image_array, index=diversity_index, no_data=NoData)

    else:
        print("Invalid input to calculate diversity index!")

