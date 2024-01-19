# merge_record

## 功能

- 将多个 record 文件转换为rosbag文件
- 对转换后的文件判断是否合并成一个rosbag文件
- 支持批量转换

## Usage

`records`文件夹结构

```bash
records
├── scene1
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
├── scene2
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
```

执行命令,生成转换脚本

```bash
apk merge record -i ./records # 仅生成配置文件
```

生成转换脚本后文件夹结构

```bash
records
├── convert.sh
├── bags
│   ├── scene1
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.pb.txt
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.pb.txt
│   ├── scene2
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.pb.txt
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.pb.txt
├── scene1
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
├── scene2
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
```

执行转换脚本

```bash
./convert.sh
```

转换后文件夹结构

```bash
records
├── convert.sh
├── bags
│   ├── scene1
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.bag
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.bag
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.pb.txt
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.pb.txt
│   ├── scene2
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.bag
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.bag
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.pb.txt
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.pb.txt
├── scene1
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
├── scene2
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
```

合并每个scene下的rosbag文件

```bash
apk merge bag -i ./bags -m explicit
```

合并后文件夹结构

```bash
records
├── scene1.bag
├── scene2.bag
├── convert.sh
├── bags
│   ├── scene1
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.bag
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.bag
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.pb.txt
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.pb.txt
│   ├── scene2
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.bag
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.bag
│   │   ├── YC800B01-N1-0001-20240111165611.record.00411.record.pb.txt
│   │   └── YC800B01-N1-0001-20240111165628.record.00412.record.pb.txt
├── scene1
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
├── scene2
│   ├── YC800B01-N1-0001-20240111165611.record.00411.record
│   └── YC800B01-N1-0001-20240111165628.record.00412.record
```

### 详解

- `-i` 输入文件夹路径，该文件路径下包含很多record文件

在执行该命令后：

- 会在record的文件夹下创建一个 `bags`文件夹，在`bags`文件夹下会创建多个文件夹，文件夹的名称是record的名称，这些文件夹包含每一个record对应转换为rosbag的配置文件该文件用于配置转换的参数
- 此外还会在bags同级文件夹下生成一个 `convert.sh` 的转换脚本，该脚本用于批量转换 record2ros
