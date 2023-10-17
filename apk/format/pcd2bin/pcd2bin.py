"""
Author: windzu windzu1@gmail.com
Date: 2023-09-09 18:58:55
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-10 15:38:58
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

import os

from pypcd import pypcd
from rich.progress import track


class Pcd2Bin:
    def __init__(
        self,
        input,
        output_dims,
        output,
    ):
        self.input = input
        self.output_dims = output_dims
        self.output = output

        self.file_list = self.get_file_list()

        # make output dir
        if not os.path.exists(self.output):
            os.makedirs(self.output)

    def get_file_list(self):
        if os.path.isdir(self.input):
            file_list = os.listdir(self.input)
            file_list = [os.path.join(self.input, file_name) for file_name in file_list]
        else:
            file_list = [self.input]

        # filter file_list with .bin suffix
        file_list = [file_name for file_name in file_list if file_name[-4:] == ".pcd"]

        return file_list

    def run(self):
        for pcd_file in track(self.file_list):
            bin_file = pcd_file.split("/")[-1][:-4] + ".bin"
            bin_file = os.path.join(self.output, bin_file)

            pc = pypcd.PointCloud.from_path(pcd_file)
            pc.save_bin(bin_file, self.output_dims)
            print("save bin file to: ", bin_file)
