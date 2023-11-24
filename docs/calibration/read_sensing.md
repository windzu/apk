# Read Sensing
>
> read sensing camera otp info

## Usage

### support camera

- SG1-OX01F10C
- SG2-AR0233C

```bash
apk calibration read_sensing --camera ${camera} --i2c_bus ${i2c_bus} --i2c_addr ${i2c_addr}
```

example:

```bash
apk calibration read_sensing --camera SG1-OX01F10C --i2c_bus 9 --i2c_addr 36
```
