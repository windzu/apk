# Read Sensing
>
> read sensing camera otp info

## Usage

### support camera

- SG1-OX01F10C
- SG2-AR0233C

## 参数说明

- `--camera` 相机型号, 从支持的相机型号中筛选
- `--i2c_bus` i2c bus number , 在不同的域控制器上这个地址不一样,要结合实际情况填写
- `--i2c_addr` i2c address, 在不同的域控制器上这个地址不一样,要结合实际情况填写

```bash
apk calibration read_sensing --camera ${camera} --i2c_bus ${i2c_bus} --i2c_addr ${i2c_addr}
```

example:

```bash
apk calibration read_sensing --camera SG1-OX01F10C --i2c_bus 9 --i2c_addr 36
```

## 附件

- 米文orin nx
  - i2c_bus 2
  - i2c_addr 0x1a(7bit表示法)
- 天准 xavier
  - i2c_bus 9
  - i2c_addr 0x36(8bit表示法)
