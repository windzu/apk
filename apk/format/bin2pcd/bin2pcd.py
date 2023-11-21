"""
Author: wind windzu1@gmail.com
Date: 2023-11-07 17:15:41
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-20 19:06:52
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
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


class Bin2Pcd:
    def __init__(
        self,
        input,
        input_dims,
        output,
    ):
        self.input = input
        self.input_dims = input_dims
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
        file_list = [file_name for file_name in file_list if file_name[-4:] == ".bin"]

        return file_list

    def run(self):
        for bin_file in track(self.file_list):
            pcd_file = bin_file.split("/")[-1][:-4] + ".pcd"
            pcd_file = os.path.join(self.output, pcd_file)

            # check file valid by check file size
            if os.path.getsize(bin_file) == 0:
                print("file size is 0, skip: ", bin_file)
                continue

            pc = pypcd.PointCloud.from_bin(bin_file, format=self.input_dims)
            pc.save_pcd(pcd_file, compression="binary_compressed")
            print("save pcd file to: ", pcd_file)
