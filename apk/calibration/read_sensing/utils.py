import numpy as np


def convert_6k_to_2k(
    width,
    height,
    fx,
    fy,
    cx,
    cy,
    k_list,
    step=4,
):
    assert len(k_list) == 6

    k1 = k_list[0]
    k2 = k_list[1]
    k3 = k_list[2]
    k4 = k_list[3]
    k5 = k_list[4]
    k6 = k_list[5]

    camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    # create_dataset
    camera_matrix_I = np.array(np.matrix(camera_matrix).I)
    data = []
    for w in range(0, width, step):
        for h in range(0, height, step):
            x_ = (
                w * camera_matrix_I[0][0]
                + h * camera_matrix_I[0][1]
                + camera_matrix_I[0][2]
            )
            y_ = (
                w * camera_matrix_I[1][0]
                + h * camera_matrix_I[1][1]
                + camera_matrix_I[1][2]
            )
            z_ = (
                w * camera_matrix_I[2][0]
                + h * camera_matrix_I[2][1]
                + camera_matrix_I[2][2]
            )
            assert z_ == camera_matrix_I[2][2]
            x = x_ / z_
            y = y_ / z_
            r2 = pow(x, 2) + pow(y, 2)
            res = (1 + ((k3 * r2 + k2) * r2 + k1) * r2) / (
                1 + ((k6 * r2 + k5) * r2 + k4) * r2
            )
            data.append([r2, pow(r2, 2), res - 1])
    data = np.array(data)

    # 采样出的点的r r^2
    X = data[:, :2]
    # 径向畸变的程度
    Y = data[:, 2]
    Y = Y[:, np.newaxis]
    # 拟合出的K 2x1维
    k = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y)

    k1 = k[0][0].tolist()
    k2 = k[1][0].tolist()

    result_k_list = [k1, k2]

    return result_k_list
