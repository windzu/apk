"""
Author: wind windzu1@gmail.com
Date: 2023-09-01 15:01:47
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-01 15:02:12
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import struct


def parse_camera_info(result):
    total_bytes = 10
    camera_info = {
        "sensor_id": "Undefined",  # 8bit 0x00:Undefined 0x52:OX01F
        "isp_id": "Undefined",  # 8bit 0x00:Undefined
        "resolution_width": 0,  # 16bit uint(Low byte first)
        "resolution_height": 0,  # 16bit uint(High byte first)
        "fps": 30,  # 8bit 0x1E:30
        "image_format": "",  # 8bit 0x01:YUYV  0x02：UYVY
        "trigger_mode": "",  # 8bit 0x01:Enable 0x02：Disable
        "embedded_data": "",  # 8bit 0x01:Enable  0x02:Disable
    }

    # check total bytes
    if len(result) != total_bytes:
        print("Error: total bytes is not correct")
        return None

    #############################
    # parse result
    #############################
    # sensor_id
    if result[0] == "0x52":
        camera_info["sensor_id"] = "OX01F"
    else:
        camera_info["sensor_id"] = "Undefined"

    # isp_id
    if result[1] == "0x00":
        camera_info["isp_id"] = "Undefined"
    else:
        camera_info["isp_id"] = "Undefined"

    # resolution_width
    camera_info["resolution_width"] = int(result[2], 16) + int(result[3], 16) * 2**8

    # resolution_height
    camera_info["resolution_height"] = int(result[4], 16) + int(result[5], 16) * 2**8

    # fps
    camera_info["fps"] = int(result[6], 16)

    # image_format
    if result[7] == "0x01":
        camera_info["image_format"] = "YUYV"
    elif result[7] == "0x02":
        camera_info["image_format"] = "UYVY"
    else:
        camera_info["image_format"] = "Undefined"

    # trigger_mode
    if result[8] == "0x01":
        camera_info["trigger_mode"] = "Enable"
    elif result[8] == "0x02":
        camera_info["trigger_mode"] = "Disable"
    else:
        camera_info["trigger_mode"] = "Undefined"

    # embedded_data
    if result[9] == "0x01":
        camera_info["embedded_data"] = "Enable"
    elif result[9] == "0x02":
        camera_info["embedded_data"] = "Disable"
    else:
        camera_info["embedded_data"] = "Undefined"

    return camera_info


def parse_lens_info(result):
    total_bytes = 9
    lens_info = {
        "fov": 0,  # 8bit uint
        "focal_length": 0,  # 32bit float
        "F": 0,  # 32bit float
    }

    # check total bytes
    if len(result) != total_bytes:
        print("Error: total bytes is not correct")
        return None

    #############################
    # parse result
    #############################
    def hex_to_float(hex_values):
        # 将前四个16进制值组合成一个字节串
        # byte_string = bytes([hex_values[i] for i in range(4)])
        # byte_string = bytes(int(val,16) for val in hex_values[:4])
        byte_string = bytes(
            int(val, 16) if isinstance(val, str) else val for val in hex_values[:4]
        )

        # 使用struct模块将这个字节串解析为浮点数
        return struct.unpack("<f", byte_string)[0]

    # fov
    lens_info["fov"] = int(result[0], 16)
    lens_info["focal_length"] = hex_to_float(result[1:5])
    lens_info["F"] = hex_to_float(result[5:9])

    return lens_info


def parse_serial_number(result):
    total_bytes = 7
    serial_number = {
        "year": 0,  # 8bit uint
        "month": 0,  # 8bit uint
        "day": 0,  # 8bit uint
        "serial": 0,  # 32bit uint
    }

    # check total bytes
    if len(result) != total_bytes:
        print("Error: total bytes is not correct")
        return None

    #############################
    # parse result
    #############################
    # year
    serial_number["year"] = int(result[0], 16)

    # month
    serial_number["month"] = int(result[1], 16)

    # day
    serial_number["day"] = int(result[2], 16)

    # serial
    def hex_list_to_decimal(lst):
        # 反转列表
        reversed_lst = lst[::-1]

        # 将列表中的每个元素连接为一个字符串
        # hex_string = ''.join(reversed_lst)
        # 移除"0x"并将列表中的每个元素连接为一个字符串
        hex_string = "".join([item[2:] for item in reversed_lst])

        # 将十六进制字符串转换为十进制整数
        decimal_value = int(hex_string, 16)

        return decimal_value

    serial_number["serial"] = hex_list_to_decimal(result[3:7])

    return serial_number


def parse_camera_matrix_info(result):
    total_bytes = 133
    camera_matrix_info = {
        "image_width": 0,  # 16bit uint(High byte first)
        "image_height": 0,  # 16bit uint(High byte first)
        "model": "",  # 8bit 0x01:Pinhole 0x02:fisheye 0x03:C'Mei
        "fx": 0,  # 64bit double
        "fy": 0,  # 64bit double
        "cx": 0,  # 64bit double
        "cy": 0,  # 64bit double
        "pinhole_k1": 0,  # 64bit double
        "pinhole_k2": 0,  # 64bit double
        "pinhole_p1": 0,  # 64bit double
        "pinhole_p2": 0,  # 64bit double
        "pinhole_k3": 0,  # 64bit double
        "pinhole_k4": 0,  # 64bit double
        "pinhole_k5": 0,  # 64bit double
        "pinhole_k6": 0,  # 64bit double
        "fisheye_k1": 0,  # 64bit double
        "fisheye_k2": 0,  # 64bit double
        "fisheye_k3": 0,  # 64bit double
        "fisheye_k4": 0,  # 64bit double
    }

    # check total bytes
    if len(result) != total_bytes:
        print("Error: total bytes is not correct")
        return None

    #############################
    # parse result
    #############################
    def hex_to_double(hex_values):
        # 将前八个16进制值组合成一个字节串
        byte_string = bytes(
            int(val, 16) if isinstance(val, str) else val for val in hex_values[:8]
        )

        # 使用struct模块将这个字节串解析为浮点数
        return struct.unpack("<d", byte_string)[0]

    # image_width
    camera_matrix_info["image_width"] = int(result[0], 16) + int(result[1], 16) * 2**8

    # image_height
    camera_matrix_info["image_height"] = (
        int(result[2], 16) + int(result[3], 16) * 2**8
    )

    # model
    if result[4] == "0x01":
        camera_matrix_info["model"] = "Pinhole"
    elif result[4] == "0x02":
        camera_matrix_info["model"] = "fisheye"
    elif result[4] == "0x03":
        camera_matrix_info["model"] = "C'Mei"
    else:
        camera_matrix_info["model"] = "Undefined"

    # fx
    camera_matrix_info["fx"] = hex_to_double(result[5:13])

    # fy
    camera_matrix_info["fy"] = hex_to_double(result[13:21])

    # cx
    camera_matrix_info["cx"] = hex_to_double(result[21:29])

    # cy
    camera_matrix_info["cy"] = hex_to_double(result[29:37])

    # pinhole_k1
    camera_matrix_info["pinhole_k1"] = hex_to_double(result[37:45])

    # pinhole_k2
    camera_matrix_info["pinhole_k2"] = hex_to_double(result[45:53])

    # pinhole_p1
    camera_matrix_info["pinhole_p1"] = hex_to_double(result[53:61])

    # pinhole_p2
    camera_matrix_info["pinhole_p2"] = hex_to_double(result[61:69])

    # pinhole_k3
    camera_matrix_info["pinhole_k3"] = hex_to_double(result[69:77])

    # pinhole_k4
    camera_matrix_info["pinhole_k4"] = hex_to_double(result[77:85])

    # pinhole_k5
    camera_matrix_info["pinhole_k5"] = hex_to_double(result[85:93])

    # pinhole_k6
    camera_matrix_info["pinhole_k6"] = hex_to_double(result[93:101])

    # fisheye_k1
    camera_matrix_info["fisheye_k1"] = hex_to_double(result[101:109])

    # fisheye_k2
    camera_matrix_info["fisheye_k2"] = hex_to_double(result[109:117])

    # fisheye_k3
    camera_matrix_info["fisheye_k3"] = hex_to_double(result[117:125])

    # fisheye_k4
    camera_matrix_info["fisheye_k4"] = hex_to_double(result[125:133])

    return camera_matrix_info
