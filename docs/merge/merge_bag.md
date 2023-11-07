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

### Example

文件夹结构如下：

```bash
# example 1
bags
├── 0.bag
└── 1.bag


# example 2
bags
├── bags_0
│   ├── 0.bag
│   └── 1.bag
└── bags_1
    ├── 0.bag
    └── 1.bag
```

执行

```bash
apk merge bag -i ./bags
```

文件夹结构如下：

```bash
# example 1
bags
├── 0.bag
├── 1.bag
└── output.bag

# example 2
bags
├── bags_0
│   ├── 0.bag
│   ├── 1.bag
│   └── output.bag
└── bags_1
    ├── 0.bag
    ├── 1.bag
    └── output.bag
```
