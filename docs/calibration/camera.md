<!--
 * @Author: windzu windzu1@gamil.com
 * @Date: 2023-09-08 10:54:30
 * @LastEditors: wind windzu1@gmail.com
 * @LastEditTime: 2023-09-08 13:17:18
 * @Description: 
 * Copyright (c) 2023 by windzu, All Rights Reserved. 
-->
# 相机内参标定

## 功能
- 标定相机内参
- 支持鱼眼和针孔相机
- 生成校正后结果

## 提供两种使用模式
- 输入参数
- 输入配置文件路径

### 输入参数的使用例子

```bash
ycpk calibration camera --camera_model fisheye --size 11x8 --square 0.045 --image_dir ./images
```

### 输入配置文件的使用例子

```bash
ycpk calibration camera --config ./config.yaml
```

config.yaml
```yaml
camera_model: fisheye
size: 11x8
square: 0.045
image_dir: ./images
```

### 参说说明
- camera_model：相机模型，支持`pinhole`和`fisheye`
- size：标定板尺寸，格式为`width x height`
- square：标定板方格大小，单位为米
- image_dir：标定图片所在文件夹


### 标定结果
标定结束后会在对应文件夹内生成一个
- `result.yaml` : 标定结果
- `undistort_images` : 去畸变后的图像文件夹

标定结果格式如下
```yaml
image_width: 1280
image_height: 720
camera_name: narrow_stereo/left
camera_matrix:
  rows: 3
  cols: 3
  data: [322.54209,   0.0586 , 641.87062,
           0.     , 321.49751, 326.48946,
           0.     ,   0.     ,   1.     ]
distortion_model: equidistant
distortion_coefficients:
  rows: 1
  cols: 4
  data: [0.057458, 0.038535, -0.025005, 0.004014]
rectification_matrix:
  rows: 3
  cols: 3
  data: [1., 0., 0.,
         0., 1., 0.,
         0., 0., 1.]
projection_matrix:
  rows: 3
  cols: 4
  data: [322.54209,   0.0586 , 641.87062,   0.     ,
           0.     , 321.49751, 326.48946,   0.     ,
           0.     ,   0.     ,   1.     ,   0.     ]

```
标定结果解释
- image_width：图像宽度
- image_height：图像高度
- camera_name：相机名称(目前固定为`narrow_stereo/left`)
- camera_matrix：相机内参矩阵
- distortion_model：畸变模型
- distortion_coefficients：畸变系数
- rectification_matrix：矫正矩阵
- projection_matrix：投影矩阵