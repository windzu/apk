"""
Author: wind windzu1@gmail.com
Date: 2023-11-14 15:14:14
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-14 18:36:55
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
"""
Author: wind windzu1@gmail.com
Date: 2023-10-30 20:29:38
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-11-03 16:49:24
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""

import os
import subprocess
import time

import yaml

from .common import SUPPORT_CAMERA_INFO_DICT
from .parse_result import (
    parse_camera_info,
    parse_camera_matrix_info,
    parse_lens_info,
    parse_serial_number,
)
from .utils import convert_6k_to_2k


class SensingReader:
    def __init__(
        self,
        camera_model,
        i2c_bus,
        i2c_addr,
    ):
        self.camera_model = camera_model
        self.CAMERA_INFO_DICT = SUPPORT_CAMERA_INFO_DICT[camera_model]
        self.i2c_bus = i2c_bus
        self.i2c_addr = i2c_addr
        self.need_read_fields = {
            "camera_info": {
                "start_address": "0x00000",
                "data_length": 10,
            },
            "lens_info": {
                "start_address": "0x00020",
                "data_length": 9,
            },
            "serial_number": {
                "start_address": "0x00040",
                "data_length": 7,
            },
            "camera_matrix_info": {
                "start_address": "0x00060",
                "data_length": 133,
            },
        }

        self.result_info_dict = {}

        self.flash_read_otp_data_command = [
            "w3@0xI2C_ADDR 0x81 0x81 0x00",  # disable CRC
            "w3@0xI2C_ADDR 0xe4 0x00 0x81",  # Command ID
            "w3@0xI2C_ADDR 0xe4 0x01 0x00",  # Command Mode
            "w3@0xI2C_ADDR 0xe4 0x02 0x00",  # Para Length
            "w3@0xI2C_ADDR 0xe4 0x03 0x05",  # Para Length
            "w3@0xI2C_ADDR 0xe4 0x04 0x12",  # Read command
            "w3@0xI2C_ADDR 0xe4 0x05 0xXX",  # Read start address High byte[23:16]
            "w3@0xI2C_ADDR 0xe4 0x06 0xXX",  # Read start address middle byte[15:8]
            "w3@0xI2C_ADDR 0xe4 0x07 0xXX",  # Read start address low byte[7:0]
            "w3@0xI2C_ADDR 0xe4 0x08 0xXX",  # Read data length high byte[15:8]
            "w3@0xI2C_ADDR 0xe4 0x09 0xXX",  # Read data length low byte[7:0]
            "w3@0xI2C_ADDR 0x81 0x60 0x01",  # Trigger
            "w2@0xI2C_ADDR 0xE7 0x00 rxx",  # Read data
        ]

        self.eeprom_read_otp_data_command = [
            "w2@0xI2C_ADDR 0x12 0x34 rxx",  # Read data
        ]

    def read(self):
        # 1. calculate new address
        self.need_read_fields = self.calculate_new_addr()

        # 2. read otp data
        result_dict = {}
        for info_type, command_dict in self.need_read_fields.items():
            result_list = self.get_otp_data(command_dict)
            if len(result_list) > 0:
                result = result_list[-1]
                result_dict[info_type] = result.split("\n")[0].split(" ")
        self.parse_result(result_dict)

        # 4. check result_info_dict
        self.check_result_info_dict()

        # 5. save result
        self.save_result()

    def parse_result(self, result_dict):
        result_info_dict = {}
        for info_type, result in result_dict.items():
            if info_type == "camera_info":
                info = parse_camera_info(result)
                result_info_dict[info_type] = info
            elif info_type == "lens_info":
                info = parse_lens_info(result)
                result_info_dict[info_type] = info
            elif info_type == "serial_number":
                info = parse_serial_number(result)
                result_info_dict[info_type] = info
            elif info_type == "camera_matrix_info":
                info = parse_camera_matrix_info(result)
                result_info_dict[info_type] = info
            else:
                print("Unknow info_type : ", info_type)

        self.result_info_dict = result_info_dict

    def calculate_new_addr(self):
        addr_offset = str(self.CAMERA_INFO_DICT["addr_offset"])
        need_read_fields = self.need_read_fields.copy()

        # iter need_read_fields
        for key, value in need_read_fields.items():
            # example :
            #   start_address : 0x00000
            #   addr_offset : 0x10000
            #   new_start_address : 0x10000
            start_address = str(value["start_address"])
            new_start_address = hex(int(start_address, 16) + int(addr_offset, 16))
            # format new_start_address to 0xXXXXXX
            new_start_address = new_start_address.replace("0x", "")
            new_start_address = new_start_address.zfill(6)
            new_start_address = "0x" + new_start_address

            value["start_address"] = new_start_address

        return need_read_fields

    @staticmethod
    def i2c_transfer(i2c_bus, i2c_addr, command_list):
        cmd_base = ["sudo", "i2ctransfer", "-f", "-y", i2c_bus]
        cmd_base_str = " ".join(cmd_base)

        result_list = []

        for command in command_list:
            command = command.replace("0xI2C_ADDR", f"0x{i2c_addr}")
            full_command_str = cmd_base_str + " " + command

            try:
                result = subprocess.run(
                    full_command_str.split(),
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )
                if result.stdout:
                    result_list.append(result.stdout)
            except subprocess.CalledProcessError as e:
                pass

            time.sleep(0.01)

        return result_list

    @staticmethod
    def get_remap_registers_command():
        # 寄存器映射
        remap_registers_command = [
            "w3@0xI2C_ADDR 0xa1 0x0a 0x00",
            "w3@0xI2C_ADDR 0xa1 0x1e 0x7f",
            "w3@0xI2C_ADDR 0xa1 0x1d 0x00",
            "w3@0xI2C_ADDR 0xa1 0x10 0x80",
            "w3@0xI2C_ADDR 0xa1 0x0f 0x18",
            "w3@0xI2C_ADDR 0xa1 0x0e 0x4c",
            "w3@0xI2C_ADDR 0xa1 0x0d 0x00",
        ]
        return remap_registers_command

    @staticmethod
    def get_load_flash_command():
        # 加载flash
        load_flash_command = [
            "w3@0xI2C_ADDR 0x81 0x81 0x00",
            "w3@0xI2C_ADDR 0xe4 0x00 0x81",  # cmd id
            "w3@0xI2C_ADDR 0xe4 0x01 0x00",  # cmd mode:loop
            "w3@0xI2C_ADDR 0xe4 0x02 0x00",  #
            "w3@0xI2C_ADDR 0xe4 0x03 0x01",  # cmd len
            "w3@0xI2C_ADDR 0xe4 0x04 0x15",  # write SF
            "w3@0xI2C_ADDR 0xe4 0x10 0x33",
            "w3@0xI2C_ADDR 0xe4 0x11 0x44",  # crc
            "w3@0xI2C_ADDR 0x81 0x60 0x01",
        ]
        return load_flash_command

    def get_otp_data(self, command_dict):
        # 1. 根据otp存储介质选择不同的读取命令和方式
        storage_medium = self.CAMERA_INFO_DICT["storage_medium"].lower()
        if storage_medium == "flash":
            # NOTE: 读取flash需要先进行触发和加载flash
            # remap registers
            remap_registers_command = self.get_remap_registers_command()
            self.i2c_transfer(self.i2c_bus, self.i2c_addr, remap_registers_command)

            # load flash
            load_flash_command = self.get_load_flash_command()
            self.i2c_transfer(self.i2c_bus, self.i2c_addr, load_flash_command)

            read_otp_data_command = self.flash_read_otp_data_command.copy()
            read_otp_data_command = self.get_read_flash_otp_data_command(
                read_otp_data_command,
                command_dict["start_address"],
                command_dict["data_length"],
            )
        elif storage_medium == "eeprom":
            read_otp_data_command = self.eeprom_read_otp_data_command.copy()
            read_otp_data_command = self.get_read_eeprom_otp_data_command(
                read_otp_data_command,
                command_dict["start_address"],
                command_dict["data_length"],
            )
        else:
            raise Exception("storage_medium error")

        # 2. 执行读取命令
        result_list = self.i2c_transfer(
            self.i2c_bus,
            self.i2c_addr,
            read_otp_data_command,
        )

        return result_list

    @staticmethod
    def get_read_flash_otp_data_command(
        read_otp_data_command,
        start_address,
        data_length,
    ):
        """获取读取FLASH的OTP数据的命令
        读取数据分为以下几个步骤:
            1. 设置寄存器进入读取OTP数据模式
            2. 设置读取OTP数据的起始地址
            3. 设置读取OTP数据的长度
            4. 触发读取OTP数据
            5. 读取OTP数据(也需要设置读取数据的长度)
        """

        # - update start address 6 7 8
        # - update data length 9 10
        def parse_start_address(address):
            """将输入的地址转换为3段8位的16进制的列表
            example: 0x123456 -> 0x12 0x34 0x56
            """
            address = address.replace("0x", "")
            address = address.zfill(6)
            return [f"0x{address[i:i+2]}" for i in range(0, 6, 2)]

        def parse_data_length(data_length):
            """将输入的数据长度转换为2段8位的16进制的列表
            example: 10 -> 0x00 0x0A
            """
            # convert to hex
            data_length = hex(data_length)
            data_length = data_length.replace("0x", "")
            data_length = data_length.zfill(4)
            return [f"0x{data_length[i:i+2]}" for i in range(0, 4, 2)]

        start_address_list = parse_start_address(start_address)
        data_length_list = parse_data_length(data_length)

        for i in range(3):
            read_otp_data_command[6 + i] = read_otp_data_command[6 + i].replace(
                "0xXX", start_address_list[i]
            )
        for i in range(2):
            read_otp_data_command[9 + i] = read_otp_data_command[9 + i].replace(
                "0xXX", data_length_list[i]
            )
        read_otp_data_command[12] = read_otp_data_command[12].replace(
            "rxx", f"r{data_length}"
        )

        return read_otp_data_command

    @staticmethod
    def get_read_eeprom_otp_data_command(
        read_otp_data_command,
        start_address,
        data_length,
    ):
        def parse_start_address(address):
            """将输入的地址转换为2段8位的16进制的列表
            example: 0x003456 -> 0x34 0x56
            """
            address = address.replace("0x", "")
            address = address.zfill(6)

            assert address[0] == "0" and address[1] == "0"
            return [f"0x{address[i:i+2]}" for i in range(2, 6, 2)]

        assert len(read_otp_data_command) == 1
        assert len(start_address) == 8

        start_address_list = parse_start_address(start_address)

        read_otp_data_command[0] = read_otp_data_command[0].replace(
            "0x12", start_address_list[0]
        )
        read_otp_data_command[0] = read_otp_data_command[0].replace(
            "0x34", start_address_list[1]
        )

        read_otp_data_command[0] = read_otp_data_command[0].replace(
            "rxx", f"r{data_length}"
        )

        return read_otp_data_command

    def check_result_info_dict(self):
        # check camera_info
        if "camera_info" in self.result_info_dict.keys():
            if "sensor_id" in self.result_info_dict["camera_info"].keys():
                if (
                    self.result_info_dict["camera_info"]["sensor_id"]
                    == self.CAMERA_INFO_DICT["sensor_id"]
                ):
                    # print("sensor_id check pass") in green color
                    print("\033[1;32m 1. sensor_id check pass \033[0m")
                else:
                    print(self.result_info_dict)
                    raise Exception("sensor_id check fail ")
            else:
                raise Exception("sensor_id not in camera_info")
        else:
            raise Exception("camera_info not in result_info_dict")

        # check camera_matrix_info
        if "camera_matrix_info" in self.result_info_dict.keys():
            camera_matrix_info = self.result_info_dict["camera_matrix_info"]
            fx = camera_matrix_info["fx"]
            fy = camera_matrix_info["fy"]
            cx = camera_matrix_info["cx"]
            cy = camera_matrix_info["cy"]
            # fx and fy should be in the range of 0 to 100000
            if fx > 0 and fx < 100000 and fy > 0 and fy < 100000:
                # print("fx and fy check pass") in green color
                print("\033[1;32m 2. fx and fy check pass \033[0m")
            else:
                raise Exception("fx and fy check fail")
        else:
            raise Exception("camera_matrix_info not in result_info_dict")

        print("\033[1;32m 3. check pass \033[0m")
        print(self.result_info_dict)

    def save_result(self):
        # 1. transfer result
        result_info_dict = self.transfer_result()

        # 2. save result
        self.save_result_info_dict_to_yaml(result_info_dict)
        self.save_result_info_dict_to_sensor_param(result_info_dict)

    def transfer_result(self):
        k_list = []
        p_list = []
        camera_matrix_info = self.result_info_dict["camera_matrix_info"]
        image_width = camera_matrix_info["image_width"]
        image_height = camera_matrix_info["image_height"]
        fx = camera_matrix_info["fx"]
        fy = camera_matrix_info["fy"]
        cx = camera_matrix_info["cx"]
        cy = camera_matrix_info["cy"]
        model = camera_matrix_info["model"].lower()
        # judge camera is fisheye or pinhole
        if model == "pinhole":
            k_list.append(camera_matrix_info["pinhole_k1"])
            k_list.append(camera_matrix_info["pinhole_k2"])
            k_list.append(camera_matrix_info["pinhole_k3"])
            k_list.append(camera_matrix_info["pinhole_k4"])
            k_list.append(camera_matrix_info["pinhole_k5"])
            k_list.append(camera_matrix_info["pinhole_k6"])
            p_list.append(camera_matrix_info["pinhole_p1"])
            p_list.append(camera_matrix_info["pinhole_p2"])

            k_list = convert_6k_to_2k(
                width=image_width,
                height=image_height,
                fx=fx,
                fy=fy,
                cx=cx,
                cy=cy,
                k_list=k_list,
            )

        elif model == "fisheye":
            k_list.append(camera_matrix_info["fisheye_k1"])
            k_list.append(camera_matrix_info["fisheye_k2"])
            k_list.append(camera_matrix_info["fisheye_k3"])
            k_list.append(camera_matrix_info["fisheye_k4"])
        else:
            raise Exception("camera_matrix_info model error")

        result_info_dict = {}
        result_info_dict["camera_info"] = self.result_info_dict["camera_info"]
        result_info_dict["lens_info"] = self.result_info_dict["lens_info"]
        result_info_dict["camera_matrix_info"] = {}
        result_info_dict["camera_matrix_info"]["image_width"] = image_width
        result_info_dict["camera_matrix_info"]["image_height"] = image_height
        result_info_dict["camera_matrix_info"]["fx"] = fx
        result_info_dict["camera_matrix_info"]["fy"] = fy
        result_info_dict["camera_matrix_info"]["cx"] = cx
        result_info_dict["camera_matrix_info"]["cy"] = cy
        result_info_dict["camera_matrix_info"]["model"] = model
        result_info_dict["camera_matrix_info"]["k_list"] = k_list
        result_info_dict["camera_matrix_info"]["p_list"] = p_list

        return result_info_dict

    def save_result_info_dict_to_yaml(self, result_info_dict):
        result_filname = "result_0.yaml"
        # check file exist ,if not exist ,create it,else filename+1
        while os.path.exists(result_filname):
            result_filename_count = int(result_filname.split(".")[0].split("_")[-1])
            result_filename_count += 1
            result_filname = "result_" + str(result_filename_count) + ".yaml"

        # save dict to yaml format
        with open(result_filname, "w") as f:
            yaml.dump(result_info_dict, f, default_flow_style=False)

    def save_result_info_dict_to_sensor_param(self, result_info_dict):
        result_filname = "result_0.txt"
        # check file exist ,if not exist ,create it,else filename+1
        while os.path.exists(result_filname):
            result_filename_count = int(result_filname.split(".")[0].split("_")[-1])
            result_filename_count += 1
            result_filname = "result_" + str(result_filename_count) + ".txt"

        sensor_param_template = """
sensor_units {
    date: date_template
    name: "cam_xxxxxxxxxxxxxxxxxxxxxxx"
    topic: "/cam_xxxxxxxxxxxxxxxxxxxxx"
    type:  type_template
    enable: true
    tf_config {
        tf_x: 0
        tf_y: 0
        tf_z: 0
        tf_roll: 0
        tf_pitch: 0
        tf_yaw: 0
    }
    camera_config {
        width : width_template
        height : height_template
        color_space : color_space_template
        video_id : "/dev/videox"
        fps : 30
        camera_intrinsics {
            K_0_0 : K_0_0_template
            K_0_1 : 0
            K_0_2 : K_0_2_template
            K_1_0 : 0
            K_1_1 : K_1_1_template
            K_1_2 : K_1_2_template
            K_2_0 : 0
            K_2_1 : 0
            K_2_2 : 1
            D_0 : D_0_template
            D_1 : D_1_template
            D_2 : D_2_template
            D_3 : D_3_template
            D_4 : D_4_template
        }
    }
}
        """
        # use result_info_dict to replace some value
        data = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        color_space = "YUYV"
        type = (
            "Pinehole"
            if result_info_dict["camera_matrix_info"]["model"].lower() == "pinhole"
            else "Fisheye"
        )
        width = result_info_dict["camera_matrix_info"]["image_width"]
        height = result_info_dict["camera_matrix_info"]["image_height"]
        K_0_0 = result_info_dict["camera_matrix_info"]["fx"]
        K_1_1 = result_info_dict["camera_matrix_info"]["fy"]
        K_0_2 = result_info_dict["camera_matrix_info"]["cx"]
        K_1_2 = result_info_dict["camera_matrix_info"]["cy"]
        if type == "Pinehole":
            D_0 = result_info_dict["camera_matrix_info"]["k_list"][0]
            D_1 = result_info_dict["camera_matrix_info"]["k_list"][1]
            D_2 = 0
            D_3 = 0
            D_4 = 0
        elif type == "Fisheye":
            D_0 = result_info_dict["camera_matrix_info"]["k_list"][0]
            D_1 = result_info_dict["camera_matrix_info"]["k_list"][1]
            D_2 = result_info_dict["camera_matrix_info"]["k_list"][2]
            D_3 = result_info_dict["camera_matrix_info"]["k_list"][3]
            D_4 = 0

        # replace value
        sensor_param_template = sensor_param_template.replace("date_template", data)
        sensor_param_template = sensor_param_template.replace("type_template", type)
        sensor_param_template = sensor_param_template.replace(
            "width_template", str(width)
        )
        sensor_param_template = sensor_param_template.replace(
            "height_template", str(height)
        )
        sensor_param_template = sensor_param_template.replace(
            "color_space_template", color_space
        )
        sensor_param_template = sensor_param_template.replace(
            "K_0_0_template", str(K_0_0)
        )
        sensor_param_template = sensor_param_template.replace(
            "K_1_1_template", str(K_1_1)
        )
        sensor_param_template = sensor_param_template.replace(
            "K_0_2_template", str(K_0_2)
        )
        sensor_param_template = sensor_param_template.replace(
            "K_1_2_template", str(K_1_2)
        )
        sensor_param_template = sensor_param_template.replace("D_0_template", str(D_0))
        sensor_param_template = sensor_param_template.replace("D_1_template", str(D_1))
        sensor_param_template = sensor_param_template.replace("D_2_template", str(D_2))
        sensor_param_template = sensor_param_template.replace("D_3_template", str(D_3))
        sensor_param_template = sensor_param_template.replace("D_4_template", str(D_4))

        # save to file
        with open(result_filname, "w") as f:
            f.write(sensor_param_template)
