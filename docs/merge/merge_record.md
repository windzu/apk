# merge_record

## 功能

- 将多个 record 文件转换为rosbag文件
- 对转换后的文件判断是否合并成一个rosbag文件
- 支持批量转换

## Usage

```bash
apk merge record -i ./records # 仅转换
apk merge record -i ./records --merge_bag # 转换并合并

```
