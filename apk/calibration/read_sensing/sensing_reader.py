"""
Author: wind windzu1@gmail.com
Date: 2023-09-01 14:48:04
LastEditors: wind windzu1@gmail.com
LastEditTime: 2023-09-01 15:02:43
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import subprocess
import time

from .parse_result import (
    parse_camera_info,
    parse_camera_matrix_info,
    parse_lens_info,
    parse_serial_number,
)


class SensingReader:
    def __init__(self, i2c_bus_and_addr_pair_list, read_otp_data_command_dict_dict):
        self.i2c_bus_and_addr_pair_list = i2c_bus_and_addr_pair_list
        self.read_otp_data_command_dict_dict = read_otp_data_command_dict_dict

    def read(self, i2c_bus_and_addr_pair_list, read_otp_data_command_dict_dict):
        for [i2c_bus, i2c_addr] in i2c_bus_and_addr_pair_list:
            # for i2c_bus in i2c_bus_list:
            #     for i2c_addr in i2c_addr_list:
            # 1. remap registers
            remap_registers_command = self.get_remap_registers_command()
            self.i2c_transfer(i2c_bus, i2c_addr, remap_registers_command)

            # 2. load flash
            load_flash_command = self.get_load_flash_command()
            self.i2c_transfer(i2c_bus, i2c_addr, load_flash_command)

            # 3. read otp data
            result_dict = {}
            for (
                info_type,
                read_otp_data_command_dict,
            ) in read_otp_data_command_dict_dict.items():
                read_otp_data_command = self.get_read_otp_data_command(
                    read_otp_data_command_dict
                )
                result_list = self.i2c_transfer(
                    i2c_bus, i2c_addr, read_otp_data_command
                )
                if len(result_list) > 0:
                    result = result_list[-1]
                    print("i2c_bus : ", i2c_bus)
                    print("i2c_addr : ", i2c_addr)
                    # print("info_type : ",info_type)
                    # print(f"start_address: {read_otp_data_command_dict['start_address']}, data_length: {read_otp_data_command_dict['data_length']}")
                    # print("result : ",result)
                    # # debug
                    print("result type : ", type(result))
                    result_dict[info_type] = result.split("\n")[0].split(" ")
            self.parse_result(result_dict)

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
        # check if have camera_info key
        if "camera_info" in result_info_dict.keys():
            # check if result_info_dict["camera_info"]["sensor_id"] is "OX01F"
            if result_info_dict["camera_info"]["sensor_id"] == "OX01F":
                print("result_info_dict : ", result_info_dict)
            # print("result_info_dict : ",result_info_dict)

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

    @staticmethod
    def get_read_otp_data_command(command_dict):
        """读取OTP数据
        读取数据分为以下几个步骤:
            1. 设置寄存器进入读取OTP数据模式
            2. 设置读取OTP数据的起始地址
            3. 设置读取OTP数据的长度
            4. 触发读取OTP数据
            5. 读取OTP数据(也需要设置读取数据的长度)
        """
        # 读取OTP数据
        read_otp_data_command = [
            "w3@0xI2C_ADDR 0x81 0x81 0x00",  # disable CRC
            "w3@0xI2C_ADDR 0xe4 0x00 0x81",  # Command ID
            "w3@0xI2C_ADDR 0xe4 0x01 0x00",  # Command Mode
            "w3@0xI2C_ADDR 0xe4 0x02 0x00",  # Para Length
            "w3@0xI2C_ADDR 0xe4 0x03 0x05",  # Para Length
            "w3@0xI2C_ADDR 0xe4 0x04 0x12",  # Read command
            "w3@0xI2C_ADDR 0xe4 0x05 0xXX",  # Read start address High byte[23:16]
            "w3@0xI2C_ADDR 0xe4 0x06 0xXX",  # Read start address middle byte[15:8]
            "w3@0xI2C_ADDR 0xe4 0x07 0xXX",  # Read start address low byte[7:0]
            "w3@0xI2C_ADDR 0xe4 0x08 0x00",  # Read data length high byte[15:8]
            "w3@0xI2C_ADDR 0xe4 0x09 0x0A",  # Read data length low byte[7:0]
            "w3@0xI2C_ADDR 0x81 0x60 0x01",  # Trigger
            "w2@0xI2C_ADDR 0xE7 0x00 rxx",  # Read data
        ]

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

        start_address_list = parse_start_address(command_dict["start_address"])
        data_length_list = parse_data_length(command_dict["data_length"])

        # update read_otp_data_command
        # - update start address 6 7 8
        # - update data length 9 10
        # - update read data length 12
        for i in range(3):
            read_otp_data_command[6 + i] = read_otp_data_command[6 + i].replace(
                "0xXX", start_address_list[i]
            )
        for i in range(2):
            read_otp_data_command[9 + i] = read_otp_data_command[9 + i].replace(
                "0xXX", data_length_list[i]
            )
        read_otp_data_command[12] = read_otp_data_command[12].replace(
            "rxx", f"r{command_dict['data_length']}"
        )

        return read_otp_data_command
