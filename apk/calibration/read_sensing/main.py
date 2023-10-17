"""
Author: wind windzu1@gmail.com
Date: 2023-08-31 16:05:20
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-08-31 16:08:35
Description: calib camera main function
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

from argparse import ArgumentParser

from .sensing_reader import SensingReader


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--camera_model",
        type=str,
        default="pinhole",
        help="pinhole or fisheye [default: pinhole]",
    )
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    i2c_bus_and_addr_pair_list = [
        ["9", "36"],
        ["10", "36"],
        ["11", "36"],
        ["12", "36"],
    ]
    read_otp_data_command_dict_dict = {
        "camera_info": {
            "start_address": "0x10000",
            "data_length": 10,
        },
        "lens_info": {
            "start_address": "0x10020",
            "data_length": 9,
        },
        "serial_number": {
            "start_address": "0x10040",
            "data_length": 7,
        },
        "camera_matrix_info": {
            "start_address": "0x10060",
            "data_length": 133,
        },
    }

    sensing_reader = SensingReader(
        i2c_bus_and_addr_pair_list, read_otp_data_command_dict_dict
    )
    sensing_reader.read()
