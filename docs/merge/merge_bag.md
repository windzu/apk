# merge_bag

## 功能

- 将多个rosbag文件合并成一个rosbag文件
- 支持批量转换

## Usage

```bash
apk merge bag -i ./bags

apk merge bag -i ./bags -o ./bags/output.bag

apk merge bag -i ./bags -o ./bags/output.bag -c lz4
```
