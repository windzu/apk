# pcd2bin

## 功能

- 将pcd格式点云转换为bin格式点云
- 支持文件夹批量转换

## 提供一种使用模式

- 输入参数

### 输入参数的使用例子

```bash
# 转换单个文件，输出到指定目录，输出文件名为test.bin
apk format pcd2bin --input ./test.pcd --output_dims xyzi --output ./

# 转换文件夹，输出到指定目录
apk format pcd2bin --input ./pcds --output_dims xyzi --output ./bins
```
