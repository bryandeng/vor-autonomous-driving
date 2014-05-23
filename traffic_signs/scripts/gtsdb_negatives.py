#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Boyuan Deng <bryanhsudeng@gmail.com>

"""
add negatives to GTSDB training set (put in TrainIJCNN2013/neg),
namely all the image files of traffic signs from "other" category.

not very useful, they are too small.
"""

import argparse
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("path",
                    help="path to GTSDB training set")
args = parser.parse_args()
train_set_root_dir = args.path
# check if it's the right directory
assert os.path.exists(os.path.join(train_set_root_dir, 'gt.txt'))


prohibitory = set([0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 15, 16])
mandatory = set([33, 34, 35, 36, 37, 38, 39, 40])
danger = set([11, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31])

other = list(set(range(43)) - (prohibitory | mandatory | danger))

neg_folder_path = os.path.join(train_set_root_dir, 'neg/')
if not os.path.exists(neg_folder_path):
    os.mkdir(neg_folder_path)

for subfolder_number in other:
    subfolder_name = str(subfolder_number).zfill(2)
    subfolder_path = os.path.join(train_set_root_dir, subfolder_name)

    for root, dirs, files in os.walk(subfolder_path):
        for name in files:
            neg_file_path = os.path.join(
                neg_folder_path, subfolder_name + '-' + name)
            shutil.copy(os.path.join(root, name), neg_file_path)
