# 图像采集

## 功能
- 预览相机图像
- s 保存当前图像至指定路径
- ctrl+c 退出

## 提供两种使用模式
- 输入参数
- 输入配置文件路径

### 输入参数的使用例子

```bash
ycpk capture camera --enable_nv --device /dev/video0 --width 1280 --height 720 --fps 30 --format UYVY --store_path ./images
```

### 输入配置文件的使用例子

```bash
ycpk capture camera --config ./config.yaml
```

config.yaml
```yaml
enable_nv: true # 是否启用nvidia硬件加速
device: /dev/video0 # 相机设备
width: 1280 # 图像宽度
height: 720 # 图像高度
fps: 30 # 帧率
format: YUY2 # 图像格式 YUY2 UYVY
store_path : ~/Downloads/capture/camera # 图像保存路径
```