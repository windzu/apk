# 点云采集

## 功能

- 订阅点云topic，保存点云至指定路径
- 支持多个topic同时订阅
- 支持自定义保存格式，支持保存为`pcd`、`bin`格式
- 支持自定义保存的通道，支持保存`xyz`、`xyzi`通道
- `s` 保存所有已订阅的点云topic的当前点云至指定路径，不同topic的点云保存在不同的文件夹下
- `q` 退出 或者 `ctrl+c` 退出

## 提供两种使用模式

- 输入参数
- 输入配置文件路径

### 输入参数的使用例子

```bash
apk capture lidar --topics '["/lidar_points/fusion", "/lidar_points/top", "/terrain_map"]' --suffix .pcd --store_dims xyzi --store_path ~/Downloads/capture/lidar
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
