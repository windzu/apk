# merge_record

## 功能

- 将多个 record 文件转换为rosbag文件
- 对转换后的文件判断是否合并成一个rosbag文件
- 支持批量转换

## Usage

```bash
apk merge record -i ./records # 仅生成配置文件
```

### 详解

- `-i` 输入文件夹路径，该文件路径下包含很多record文件

在执行该命令后：

- 会在record的文件夹下创建一个 `bags`文件夹，在`bags`文件夹下会创建多个文件夹，文件夹的名称是record的名称，这些文件夹包含每一个record对应转换为rosbag的配置文件该文件用于配置转换的参数
- 此外还会在bags同级文件夹下生成一个 `convert.sh` 的转换脚本，该脚本用于批量转换 record2ros
