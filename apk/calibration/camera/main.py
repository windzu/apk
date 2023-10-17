"""
Author: windzu windzu1@gmail.com
Date: 2023-09-07 23:32:52
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-08 00:59:58
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import os
from argparse import ArgumentParser

import cv2
import yaml

from .calibrator import CAMERA_MODEL, ChessboardInfo, MonoCalibrator


def parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--camera_model",
        type=str,
        default="pinhole",
        help="pinhole or fisheye [default: pinhole]",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="8x6",
        help="specify chessboard size as NxM [default: 8x6]",
    )
    parser.add_argument(
        "--square",
        type=str,
        default="0.108",
        help="specify chessboard square size in meters [default: 0.108]",
    )
    parser.add_argument(
        "--image_dir",
        type=str,
        default="./images",
        help="specify path to images [default: ./images]",
    )

    args = parser.parse_args(argv)
    if args.config:
        if not os.path.exists(args.config):
            print("config file is not exist")
            return args
        else:
            with open(args.config, "r") as f:
                config = yaml.safe_load(f)
                args.camera_model = config.get("camera_model", args.camera_model)
                args.size = config.get("size", args.size)
                args.square = config.get("square", args.square)
                args.image_dir = config.get("image_dir", args.image_dir)
    return args


def main(args, unknown):
    args = parse_args(unknown)

    # init camera model
    if args.camera_model == "pinhole":
        camera_model = CAMERA_MODEL.PINHOLE
    elif args.camera_model == "fisheye":
        camera_model = CAMERA_MODEL.FISHEYE

    # init chessboard
    boards = []
    info = ChessboardInfo()
    size = tuple([int(c) for c in args.size.split("x")])
    info.dim = float(args.square)
    info.n_cols = size[0]
    info.n_rows = size[1]
    boards.append(info)

    # init calib_flags
    calib_flags = 0
    calib_flags |= cv2.CALIB_FIX_K3

    # get all images path
    # check image_dir is exist
    if not os.path.exists(args.image_dir):
        print("image_dir is not exist")
        return
    image_path_list = []
    for root, dirs, files in os.walk(args.image_dir):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png"):
                image_path_list.append(os.path.join(root, file))

    calibrator = MonoCalibrator(camera_model, boards, calib_flags)
    calibrator.do_file_calibration(image_path_list)
    result = calibrator.yaml()

    # save calib result
    with open(args.image_dir + "/result.yaml", "w") as f:
        f.write(result)

    # save undistort image
    # save_path = args.image_dir + "/undistort_images"
    save_path = os.path.join(args.image_dir, "undistort_images")
    calibrator.save_undistort_images(save_path)
    print("save undistort images to : ", save_path)
    print("calib finished")
