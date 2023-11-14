<!--
 * @Author: windzu windzu1@gamil.com
 * @Date: 2023-09-08 10:54:30
 * @LastEditors: wind windzu1@gmail.com
 * @LastEditTime: 2023-11-14 15:46:47
 * @Description: 
 * Copyright (c) 2023 by windzu, All Rights Reserved. 
-->

# APK

awesome perception kit

本项目是一个感知工具集合，包含了感知一些常用的功能，比如传感器标定、数据采集、数据处理等

| Tools           | Description    |
| --------------- |:--------------:|
| capture         | 数据采集        |
| calibration     | 标定功能        |
| format          | 数据格式化      |

## Install

### 发行版安装

#### 依赖

- python3.6+
- pip3
- ros1

#### 安装

先安装 apt 依赖

```bash
sudo apt-get install libgirepository1.0-dev libcairo2-dev libglib2.0-dev
```

然后安装 apk

```bash
pip3 install apk
pip3 install apk --upgrade # 更新
```

### 开发版安装
>
> Note : 如果想使用开发版，必须通过源码安装

```bash
pip3 install --upgrade pip
git clone https://github.com/windzu/apk.git
cd apk
pip3 install -e .
```

## Usage
>
> 下面是一些简单的使用介绍，更多高级用法请参考其对应文档

```bash
apk [tools_name] [function_name] [args]
```

### Capture(数据采集)
>
> 本工具提供了一个简单的采集相机图像、点云、IMU等据的工具

| Function        | Description      |Document                           |Development progress|
| --------------- |:----------------:|:---------------------------------:|:------------------:|
| camera          | 采集相机数据       |[Doc](./docs/capture/camera.md)    |✅                  |
| lidar           | 采集点云数据       |[Doc](./docs/capture/lidar.md)     |✅                  |

### Calibration(标定)
>
> 本工具提供了相机内参标定、雷达外参标定、相机雷达联合标定等功能

| Function        | Description      |Document                                  |Development progress|
| --------------- |:----------------:|:----------------------------------------:|:------------------:|
| camera          | 相机内参标定       |[Doc](./docs/calibration/camera.md)       |✅                  |
| lidar2lidar     | 雷达外参标定       |[Doc](./docs/calibration/lidar2lidar.md)  |❎                  |
| lidar2camera    | 相机雷达外参标定    |[Doc](./docs/calibration/lidar2camera.md) |❎                  |
| read_sensing    | 读取森云相机内参    |[Doc](./docs/calibration/read_sensing.md) |❎                  |

### Format(数据格式化)
>
> 本工具提供了数据格式转化、数据集转换等功能

| Function        | Description          |Document                           |Development progress|
| --------------- |:--------------------:|:---------------------------------:|:------------------:|
| bin2pcd         | bin格式点云转pcd格式   |[Doc](./docs/format/bin2pcd.md)    |✅                  |
| pcd2bin         | pcd格式点云转bin格式   |[Doc](./docs/format/pcd2bin.md)    |✅                  |
