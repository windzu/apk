# 点云采集

## 功能

- 保存指定topic点云至指定路径
- 支持多个topic同时订阅
- 支持自定义保存格式，支持保存为`pcd`、`bin`格式
- 支持自定义保存的通道，支持保存`xyz`、`xyzi`通道
- 自动模式保存 : 通过设置保存时间间隔，自动保存点云 , 自动模式需要提供以下参数
  - file : rosbag 文件路径
  - store_interval : 保存时间间隔，单位为ms , 默认为0,当设置为0时，表示保存所有点云
- 手动模式保存 : 通过按键手动保存点云
  - `s` 保存所有已订阅的点云topic的当前点云至指定路径，不同topic的点云保存在不同的文件夹下
  - `q` 退出 或者 `ctrl+c` 退出

## 提供两种参数输入模式

- 直接提供所有必要参数
- 提供配置文件路径,所需参数在配置文件中配置

## 参数说明

- `--config` : 配置文件路径
- `--file` : rosbag 文件路径
- `--topics` : 点云topic list
- `--suffix` : 保存格式 , 支持`pcd`、`bin`格式 , 默认为`pcd`
- `--store_method` : 保存模式 , 支持`auto`、`manual`模式 , 默认为`auto`
- `--store_interval` : 保存时间间隔 , 单位为ms , 默认为0,表示保存所有点云
- `--store_dims` : 保存通道 , 支持`xyz`、`xyzi`通道 , 默认为`xyzi`
- `--store_path` : 点云保存路径

### 输入参数的使用例子

```bash
# auto mode
apk capture lidar --file xxx.bag --topics '["/lidar_points/top"]' --store_path ~/Downloads/capture/lidar

# manual mode
apk capture lidar --topics '["/lidar_points/fusion", "/lidar_points/top", "/terrain_map"]' --store_method manual --suffix .pcd --store_dims xyzi --store_path ~/Downloads/capture/lidar
```

### 输入配置文件的使用例子

```bash
apk capture lidar --config ./config.yaml
```

config.yaml

```yaml
topics: ["/lidar_points/fusion", "/lidar_points/top", "/terrain_map"] # 点云topic list
suffix: .pcd # 保存格式
store_dims: xyzi # 保存通道
store_path : ~/Downloads/capture/lidar # 点云保存路径
```
