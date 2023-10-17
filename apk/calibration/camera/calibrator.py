#!/usr/bin/env python

# import image_geometry
import math
import os
import pickle
import random
import tarfile
from enum import Enum

import cv2
import numpy.linalg
import sensor_msgs.msg
from rich.progress import track


# Supported camera models
class CAMERA_MODEL(Enum):
    PINHOLE = 0
    FISHEYE = 1


# Supported calibration patterns
class Patterns:
    Chessboard, Circles, ACircles, ChArUco = list(range(4))


class CalibrationException(Exception):
    pass


# TODO: Make pattern per-board?
class ChessboardInfo:
    def __init__(
        self,
        pattern="chessboard",
        n_cols=0,
        n_rows=0,
        dim=0.0,
        marker_size=0.0,
        aruco_dict=None,
    ):
        self.pattern = pattern
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.dim = dim
        self.marker_size = marker_size
        self.aruco_dict = None
        self.charuco_board = None
        if pattern == "charuco":
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(
                {
                    "aruco_orig": cv2.aruco.DICT_ARUCO_ORIGINAL,
                    "4x4_50": cv2.aruco.DICT_4X4_50,
                    "4x4_100": cv2.aruco.DICT_4X4_100,
                    "4x4_250": cv2.aruco.DICT_4X4_250,
                    "4x4_1000": cv2.aruco.DICT_4X4_1000,
                    "5x5_50": cv2.aruco.DICT_5X5_50,
                    "5x5_100": cv2.aruco.DICT_5X5_100,
                    "5x5_250": cv2.aruco.DICT_5X5_250,
                    "5x5_1000": cv2.aruco.DICT_5X5_1000,
                    "6x6_50": cv2.aruco.DICT_6x6_50,
                    "6x6_100": cv2.aruco.DICT_6x6_100,
                    "6x6_250": cv2.aruco.DICT_6x6_250,
                    "6x6_1000": cv2.aruco.DICT_6x6_1000,
                    "7x7_50": cv2.aruco.DICT_7x7_50,
                    "7x7_100": cv2.aruco.DICT_7x7_100,
                    "7x7_250": cv2.aruco.DICT_7x7_250,
                    "7x7_1000": cv2.aruco.DICT_7x7_1000,
                }[aruco_dict]
            )
            self.charuco_board = cv2.aruco.CharucoBoard_create(
                self.n_cols, self.n_rows, self.dim, self.marker_size, self.aruco_dict
            )


# Make all private!!!!!
def lmin(seq1, seq2):
    """Pairwise minimum of two sequences"""
    return [min(a, b) for (a, b) in zip(seq1, seq2)]


def lmax(seq1, seq2):
    """Pairwise maximum of two sequences"""
    return [max(a, b) for (a, b) in zip(seq1, seq2)]


def _pdist(p1, p2):
    """
    Distance bwt two points. p1 = (x, y), p2 = (x, y)
    """
    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))


def _get_outside_corners(corners, board):
    """
    Return the four corners of the board as a whole, as (up_left, up_right, down_right, down_left).
    """
    xdim = board.n_cols
    ydim = board.n_rows

    if (
        board.pattern != "charuco"
        and corners.shape[1] * corners.shape[0] != xdim * ydim
    ):
        raise Exception(
            "Invalid number of corners! %d corners. X: %d, Y: %d"
            % (corners.shape[1] * corners.shape[0], xdim, ydim)
        )
    if board.pattern == "charuco" and corners.shape[1] * corners.shape[0] != (
        xdim - 1
    ) * (ydim - 1):
        raise Exception(
            (
                "Invalid number of corners! %d corners. X: %d, Y: %d\n  for ChArUco boards, "
                + "_get_largest_rectangle_corners handles partial views of the target"
            )
            % (corners.shape[1] * corners.shape[0], xdim - 1, ydim - 1)
        )

    up_left = corners[0, 0]
    up_right = corners[xdim - 1, 0]
    down_right = corners[-1, 0]
    down_left = corners[-xdim, 0]

    return (up_left, up_right, down_right, down_left)


def _get_largest_rectangle_corners(corners, ids, board):
    """
    Return the largest rectangle with all four corners visible in a partial view of a ChArUco board, as (up_left,
    up_right, down_right, down_left).
    """

    # ChArUco board corner numbering:
    #
    #    9 10 11
    # ^  6  7  8
    # y  3  4  5
    #    0  1  2
    #      x >
    #
    # reference: https://docs.opencv.org/master/df/d4a/tutorial_charuco_detection.html

    # xdim and ydim are number of squares, but we're working with inner corners
    xdim = board.n_cols - 1
    ydim = board.n_rows - 1
    board_vis = [[[i * xdim + j] in ids for j in range(xdim)] for i in range(ydim)]

    best_area = 0
    best_rect = [-1, -1, -1, -1]

    for x1 in range(xdim):
        for x2 in range(x1, xdim):
            for y1 in range(ydim):
                for y2 in range(y1, ydim):
                    if (
                        board_vis[y1][x1]
                        and board_vis[y1][x2]
                        and board_vis[y2][x1]
                        and board_vis[y2][x2]
                        and (x2 - x1 + 1) * (y2 - y1 + 1) > best_area
                    ):
                        best_area = (x2 - x1 + 1) * (y2 - y1 + 1)
                        best_rect = [x1, x2, y1, y2]
    (x1, x2, y1, y2) = best_rect
    corner_ids = (y2 * xdim + x1, y2 * xdim + x2, y1 * xdim + x2, y1 * xdim + x1)
    corners = tuple(
        corners[numpy.where(ids == corner_id)[0]][0][0] for corner_id in corner_ids
    )

    return corners


def _calculate_skew(corners):
    """
    Get skew for given checkerboard detection.
    Scaled to [0,1], which 0 = no skew, 1 = high skew
    Skew is proportional to the divergence of three outside corners from 90 degrees.
    """
    # TODO Using three nearby interior corners might be more robust, outside corners occasionally
    # get mis-detected
    up_left, up_right, down_right, _ = corners

    def angle(a, b, c):
        """
        Return angle between lines ab, bc
        """
        ab = a - b
        cb = c - b
        return math.acos(
            numpy.dot(ab, cb) / (numpy.linalg.norm(ab) * numpy.linalg.norm(cb))
        )

    skew = min(1.0, 2.0 * abs((math.pi / 2.0) - angle(up_left, up_right, down_right)))
    return skew


def _calculate_area(corners):
    """
    Get 2d image area of the detected checkerboard.
    The projected checkerboard is assumed to be a convex quadrilateral,
    and the area computed as|p X q|/2;
    see http://mathworld.wolfram.com/Quadrilateral.html.
    """
    (up_left, up_right, down_right, down_left) = corners
    a = up_right - up_left
    b = down_right - up_right
    c = down_left - down_right
    p = b + c
    q = a + b
    return abs(p[0] * q[1] - p[1] * q[0]) / 2.0


def _get_corners(img, board, refine=True, checkerboard_flags=0):
    """
    Get corners for a particular chessboard for an image
    """
    h = img.shape[0]
    w = img.shape[1]
    if len(img.shape) == 3 and img.shape[2] == 3:
        mono = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        mono = img
    (ok, corners) = cv2.findChessboardCorners(
        mono,
        (board.n_cols, board.n_rows),
        flags=cv2.CALIB_CB_ADAPTIVE_THRESH
        | cv2.CALIB_CB_NORMALIZE_IMAGE
        | checkerboard_flags,
    )
    if not ok:
        return (ok, corners)

    # If any corners are within BORDER pixels of the screen edge,
    # reject the detection by setting ok to false
    # NOTE: This may cause problems with very low-resolution cameras,
    # where 8 pixels is a non-negligible fraction of the image size.
    # See http://answers.ros.org/question/3155/how-can-i-calibrate-low-resolution-cameras
    BORDER = 8
    if not all(
        [
            (BORDER < corners[i, 0, 0] < (w - BORDER))
            and (BORDER < corners[i, 0, 1] < (h - BORDER))
            for i in range(corners.shape[0])
        ]
    ):
        ok = False

    # Ensure that all corner-arrays are going from top to bottom.
    if board.n_rows != board.n_cols:
        if corners[0, 0, 1] > corners[-1, 0, 1]:
            corners = numpy.copy(numpy.flipud(corners))
    else:
        direction_corners = (corners[-1] - corners[0]) >= numpy.array([[0.0, 0.0]])

        if not numpy.all(direction_corners):
            if not numpy.any(direction_corners):
                corners = numpy.copy(numpy.flipud(corners))
            elif direction_corners[0][0]:
                corners = numpy.rot90(
                    corners.reshape(board.n_rows, board.n_cols, 2)
                ).reshape(board.n_cols * board.n_rows, 1, 2)
            else:
                corners = numpy.rot90(
                    corners.reshape(board.n_rows, board.n_cols, 2), 3
                ).reshape(board.n_cols * board.n_rows, 1, 2)

    if refine and ok:
        # Use a radius of half the minimum distance between corners.
        # This should be large enough to snap to the correct corner,
        # but not so large as to include a wrong corner in the search window.
        min_distance = float("inf")
        for row in range(board.n_rows):
            for col in range(board.n_cols - 1):
                index = row * board.n_rows + col
                min_distance = min(
                    min_distance, _pdist(corners[index, 0], corners[index + 1, 0])
                )
        for row in range(board.n_rows - 1):
            for col in range(board.n_cols):
                index = row * board.n_rows + col
                min_distance = min(
                    min_distance,
                    _pdist(corners[index, 0], corners[index + board.n_cols, 0]),
                )
        radius = int(math.ceil(min_distance * 0.5))
        cv2.cornerSubPix(
            mono,
            corners,
            (radius, radius),
            (-1, -1),
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1),
        )

    return (ok, corners)


def _get_charuco_corners(img, board, refine):
    """
    Get chessboard corners from image of ChArUco board
    """
    h = img.shape[0]
    w = img.shape[1]

    if len(img.shape) == 3 and img.shape[2] == 3:
        mono = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        mono = img

    marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(img, board.aruco_dict)
    if len(marker_corners) == 0:
        return (False, None, None)
    _, square_corners, ids = cv2.aruco.interpolateCornersCharuco(
        marker_corners, marker_ids, img, board.charuco_board
    )
    return (
        (square_corners is not None) and (len(square_corners) > 5),
        square_corners,
        ids,
    )


def _get_circles(img, board, pattern):
    """
    Get circle centers for a symmetric or asymmetric grid
    """
    h = img.shape[0]
    w = img.shape[1]
    if len(img.shape) == 3 and img.shape[2] == 3:
        mono = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        mono = img

    flag = cv2.CALIB_CB_SYMMETRIC_GRID
    if pattern == Patterns.ACircles:
        flag = cv2.CALIB_CB_ASYMMETRIC_GRID
    mono_arr = numpy.array(mono)
    (ok, corners) = cv2.findCirclesGrid(
        mono_arr, (board.n_cols, board.n_rows), flags=flag
    )

    # In symmetric case, findCirclesGrid does not detect the target if it's turned sideways. So we try
    # again with dimensions swapped - not so efficient.
    # TODO Better to add as second board? Corner ordering will change.
    if not ok and pattern == Patterns.Circles:
        (ok, corners) = cv2.findCirclesGrid(
            mono_arr, (board.n_rows, board.n_cols), flags=flag
        )

    return (ok, corners)


def _get_dist_model(dist_params, cam_model):
    # Select dist model
    if CAMERA_MODEL.PINHOLE == cam_model:
        if dist_params.size > 5:
            dist_model = "rational_polynomial"
        else:
            dist_model = "plumb_bob"
    elif CAMERA_MODEL.FISHEYE == cam_model:
        dist_model = "equidistant"
    else:
        dist_model = "unknown"
    return dist_model


# TODO self.size needs to come from CameraInfo, full resolution
class Calibrator(object):
    """
    Base class for calibration system
    """

    def __init__(
        self,
        camera_model,
        boards,
        flags=0,
        fisheye_flags=0,
        pattern=Patterns.Chessboard,
        name="",
        checkerboard_flags=cv2.CALIB_CB_FAST_CHECK,
        max_chessboard_speed=-1.0,
    ):
        self.camera_model = camera_model
        # Ordering the dimensions for the different detectors is actually a minefield...
        if pattern == Patterns.Chessboard:
            # Make sure n_cols > n_rows to agree with OpenCV CB detector output
            self._boards = [
                ChessboardInfo(
                    "chessboard",
                    max(i.n_cols, i.n_rows),
                    min(i.n_cols, i.n_rows),
                    i.dim,
                )
                for i in boards
            ]
        if pattern == Patterns.ChArUco:
            self._boards = boards
        elif pattern == Patterns.ACircles:
            # 7x4 and 4x7 are actually different patterns. Assume square-ish pattern, so n_rows > n_cols.
            self._boards = [
                ChessboardInfo(
                    "acircles", min(i.n_cols, i.n_rows), max(i.n_cols, i.n_rows), i.dim
                )
                for i in boards
            ]
        elif pattern == Patterns.Circles:
            # We end up having to check both ways anyway
            self._boards = boards

        # Set to true after we perform calibration
        self.calibrated = False
        self.calib_flags = flags
        self.fisheye_calib_flags = fisheye_flags
        self.checkerboard_flags = checkerboard_flags
        self.pattern = pattern
        # self.camera_model = CAMERA_MODEL.PINHOLE
        # self.db is list of (parameters, image) samples for use in calibration. parameters has form
        # (X, Y, size, skew) all normalized to [0,1], to keep track of what sort of samples we've taken
        # and ensure enough variety.
        self.db = []
        # For each db sample, we also record the detected corners (and IDs, if using a ChArUco board)
        self.good_corners = []
        # Set to true when we have sufficiently varied samples to calibrate
        self.goodenough = False
        self.param_ranges = [0.7, 0.7, 0.4, 0.5]
        self.name = name
        self.last_frame_corners = None
        self.last_frame_ids = None
        self.max_chessboard_speed = max_chessboard_speed

    def get_parameters(self, corners, ids, board, size):
        """
        Return list of parameters [X, Y, size, skew] describing the checkerboard view.
        """
        (width, height) = size
        Xs = corners[:, :, 0]
        Ys = corners[:, :, 1]
        if board.pattern == "charuco":
            outside_corners = _get_largest_rectangle_corners(corners, ids, board)
        else:
            outside_corners = _get_outside_corners(corners, board)
        area = _calculate_area(outside_corners)
        skew = _calculate_skew(outside_corners)
        border = math.sqrt(area)
        # For X and Y, we "shrink" the image all around by approx. half the board size.
        # Otherwise large boards are penalized because you can't get much X/Y variation.
        p_x = min(1.0, max(0.0, (numpy.mean(Xs) - border / 2) / (width - border)))
        p_y = min(1.0, max(0.0, (numpy.mean(Ys) - border / 2) / (height - border)))
        p_size = math.sqrt(area / (width * height))
        params = [p_x, p_y, p_size, skew]
        return params

    def set_cammodel(self, modeltype):
        self.camera_model = modeltype

    def is_slow_moving(self, corners, ids, last_frame_corners, last_frame_ids):
        """
        Returns true if the motion of the checkerboard is sufficiently low between
        this and the previous frame.
        """
        # If we don't have previous frame corners, we can't accept the sample
        if last_frame_corners is None:
            return False
        if ids is None:
            num_corners = len(corners)
            corner_deltas = (corners - last_frame_corners).reshape(num_corners, 2)
        else:
            corner_deltas = []
            last_frame_ids = list(last_frame_ids.transpose()[0])
            for i, c_id in enumerate(ids):
                try:
                    last_i = last_frame_ids.index(c_id)
                    corner_deltas.append(corners[i] - last_frame_corners[last_i])
                except ValueError:
                    pass
            corner_deltas = numpy.concatenate(corner_deltas)

        # Average distance travelled overall for all corners
        average_motion = numpy.average(numpy.linalg.norm(corner_deltas, axis=1))
        return average_motion <= self.max_chessboard_speed

    def is_good_sample(self, params, corners, ids, last_frame_corners, last_frame_ids):
        """
        Returns true if the checkerboard detection described by params should be added to the database.
        """
        if not self.db:
            return True

        def param_distance(p1, p2):
            return sum([abs(a - b) for (a, b) in zip(p1, p2)])

        db_params = [sample[0] for sample in self.db]
        d = min([param_distance(params, p) for p in db_params])
        # print "d = %.3f" % d #DEBUG
        # TODO What's a good threshold here? Should it be configurable?
        if d <= 0.2:
            return False

        if self.max_chessboard_speed > 0:
            if not self.is_slow_moving(
                corners, ids, last_frame_corners, last_frame_ids
            ):
                return False

        # All tests passed, image should be good for calibration
        return True

    _param_names = ["X", "Y", "Size", "Skew"]

    def compute_goodenough(self):
        if not self.db:
            return None

        # Find range of checkerboard poses covered by samples in database
        all_params = [sample[0] for sample in self.db]
        min_params = all_params[0]
        max_params = all_params[0]
        for params in all_params[1:]:
            min_params = lmin(min_params, params)
            max_params = lmax(max_params, params)
        # Don't reward small size or skew
        min_params = [min_params[0], min_params[1], 0.0, 0.0]

        # For each parameter, judge how much progress has been made toward adequate variation
        progress = [
            min((hi - lo) / r, 1.0)
            for (lo, hi, r) in zip(min_params, max_params, self.param_ranges)
        ]
        # If we have lots of samples, allow calibration even if not all parameters are green
        # TODO Awkward that we update self.goodenough instead of returning it
        self.goodenough = (len(self.db) >= 40) or all([p == 1.0 for p in progress])

        return list(zip(self._param_names, min_params, max_params, progress))

    def mk_object_points(self, boards, use_board_size=False):
        opts = []
        for i, b in enumerate(boards):
            num_pts = b.n_cols * b.n_rows
            opts_loc = numpy.zeros((num_pts, 1, 3), numpy.float32)
            for j in range(num_pts):
                opts_loc[j, 0, 0] = j // b.n_cols
                if self.pattern == Patterns.ACircles:
                    opts_loc[j, 0, 1] = 2 * (j % b.n_cols) + (opts_loc[j, 0, 0] % 2)
                else:
                    opts_loc[j, 0, 1] = j % b.n_cols
                opts_loc[j, 0, 2] = 0
                if use_board_size:
                    opts_loc[j, 0, :] = opts_loc[j, 0, :] * b.dim
            opts.append(opts_loc)
        return opts

    def get_corners(self, img, refine=True):
        """
        Use cvFindChessboardCorners to find corners of chessboard in image.

        Check all boards. Return corners for first chessboard that it detects
        if given multiple size chessboards.

        If a ChArUco board is used, the marker IDs are also returned, otherwise
        ids is None.

        Returns (ok, corners, ids, board)
        """

        for b in self._boards:
            if self.pattern == Patterns.Chessboard:
                (ok, corners) = _get_corners(img, b, refine, self.checkerboard_flags)
                ids = None
            elif self.pattern == Patterns.ChArUco:
                (ok, corners, ids) = _get_charuco_corners(img, b, refine)
            else:
                (ok, corners) = _get_circles(img, b, self.pattern)
                ids = None
            if ok:
                return (ok, corners, ids, b)
        return (False, None, None, None)

    def downsample_and_detect(self, img):
        """
        Downsample the input image to approximately VGA resolution and detect the
        calibration target corners in the full-size image.

        Combines these apparently orthogonal duties as an optimization. Checkerboard
        detection is too expensive on large images, so it's better to do detection on
        the smaller display image and scale the corners back up to the correct size.

        Returns (scrib, corners, downsampled_corners, ids, board, (x_scale, y_scale)).
        """
        # Scale the input image down to ~VGA size
        height = img.shape[0]
        width = img.shape[1]
        scale = math.sqrt((width * height) / (640.0 * 480.0))
        # scale = math.sqrt((width * height) / (width/3. * height/3.))
        if scale > 1.0:
            scrib = cv2.resize(img, (int(width / scale), int(height / scale)))
        else:
            scrib = img
        # Due to rounding, actual horizontal/vertical scaling may differ slightly
        x_scale = float(width) / scrib.shape[1]
        y_scale = float(height) / scrib.shape[0]

        if self.pattern == Patterns.Chessboard:
            # Detect checkerboard
            (ok, downsampled_corners, ids, board) = self.get_corners(scrib, refine=True)

            # Scale corners back to full size image
            corners = None
            if ok:
                if scale > 1.0:
                    # Refine up-scaled corners in the original full-res image
                    # TODO Does this really make a difference in practice?
                    corners_unrefined = downsampled_corners.copy()
                    corners_unrefined[:, :, 0] *= x_scale
                    corners_unrefined[:, :, 1] *= y_scale
                    radius = int(math.ceil(scale))
                    if len(img.shape) == 3 and img.shape[2] == 3:
                        mono = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    else:
                        mono = img
                    cv2.cornerSubPix(
                        mono,
                        corners_unrefined,
                        (radius, radius),
                        (-1, -1),
                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1),
                    )
                    corners = corners_unrefined
                else:
                    corners = downsampled_corners
        else:
            # Circle grid detection is fast even on large images
            (ok, corners, ids, board) = self.get_corners(img)
            # Scale corners to downsampled image for display
            downsampled_corners = None
            if ok:
                if scale > 1.0:
                    downsampled_corners = corners.copy()
                    downsampled_corners[:, :, 0] /= x_scale
                    downsampled_corners[:, :, 1] /= y_scale
                else:
                    downsampled_corners = corners

        return (scrib, corners, downsampled_corners, ids, board, (x_scale, y_scale))

    @staticmethod
    def lrmsg(d, k, r, p, size, camera_model):
        """Used by :meth:`as_message`.  Return a CameraInfo message for the given calibration matrices"""
        msg = sensor_msgs.msg.CameraInfo()
        msg.width, msg.height = size
        msg.distortion_model = _get_dist_model(d, camera_model)

        msg.D = numpy.ravel(d).copy().tolist()
        msg.K = numpy.ravel(k).copy().tolist()
        msg.R = numpy.ravel(r).copy().tolist()
        msg.P = numpy.ravel(p).copy().tolist()
        return msg

    @staticmethod
    def lrreport(d, k, r, p):
        print("D =", numpy.ravel(d).tolist())
        print("K =", numpy.ravel(k).tolist())
        print("R =", numpy.ravel(r).tolist())
        print("P =", numpy.ravel(p).tolist())

    @staticmethod
    def lrost(name, d, k, r, p, size):
        assert k.shape == (3, 3)
        assert r.shape == (3, 3)
        assert p.shape == (3, 4)
        calmessage = "\n".join(
            [
                "# oST version 5.0 parameters",
                "",
                "",
                "[image]",
                "",
                "width",
                "%d" % size[0],
                "",
                "height",
                "%d" % size[1],
                "",
                "[%s]" % name,
                "",
                "camera matrix",
                " ".join("%8f" % k[0, i] for i in range(3)),
                " ".join("%8f" % k[1, i] for i in range(3)),
                " ".join("%8f" % k[2, i] for i in range(3)),
                "",
                "distortion",
                " ".join("%8f" % x for x in d.flat),
                "",
                "rectification",
                " ".join("%8f" % r[0, i] for i in range(3)),
                " ".join("%8f" % r[1, i] for i in range(3)),
                " ".join("%8f" % r[2, i] for i in range(3)),
                "",
                "projection",
                " ".join("%8f" % p[0, i] for i in range(4)),
                " ".join("%8f" % p[1, i] for i in range(4)),
                " ".join("%8f" % p[2, i] for i in range(4)),
                "",
            ]
        )
        assert len(calmessage) < 525, "Calibration info must be less than 525 bytes"
        return calmessage

    @staticmethod
    def lryaml(name, d, k, r, p, size, cam_model):
        def format_mat(x, precision):
            return "[%s]" % (
                numpy.array2string(
                    x, precision=precision, suppress_small=True, separator=", "
                )
                .replace("[", "")
                .replace("]", "")
                .replace("\n", "\n        ")
            )

        dist_model = _get_dist_model(d, cam_model)

        assert k.shape == (3, 3)
        assert r.shape == (3, 3)
        assert p.shape == (3, 4)
        calmessage = "\n".join(
            [
                "image_width: %d" % size[0],
                "image_height: %d" % size[1],
                "camera_name: " + name,
                "camera_matrix:",
                "  rows: 3",
                "  cols: 3",
                "  data: " + format_mat(k, 5),
                "distortion_model: " + dist_model,
                "distortion_coefficients:",
                "  rows: 1",
                "  cols: %d" % d.size,
                "  data: [%s]" % ", ".join("%8f" % x for x in d.flat),
                "rectification_matrix:",
                "  rows: 3",
                "  cols: 3",
                "  data: " + format_mat(r, 8),
                "projection_matrix:",
                "  rows: 3",
                "  cols: 4",
                "  data: " + format_mat(p, 5),
                "",
            ]
        )
        return calmessage

    def do_save(self):
        filename = "/tmp/calibrationdata.tar.gz"
        tf = tarfile.open(filename, "w:gz")
        self.do_tarfile_save(tf)  # Must be overridden in subclasses
        tf.close()
        print(("Wrote calibration data to", filename))


def image_from_archive(archive, name):
    """
    Load image PGM file from tar archive.

    Used for tarfile loading and unit test.
    """
    member = archive.getmember(name)
    imagefiledata = numpy.fromstring(archive.extractfile(member).read(), numpy.uint8)
    imagefiledata.resize((1, imagefiledata.size))
    return cv2.imdecode(imagefiledata, cv2.IMREAD_COLOR)


class MonoCalibrator(Calibrator):
    """
    Calibration class for monocular cameras::

        images = [cv2.imread("mono%d.png") for i in range(8)]
        mc = MonoCalibrator()
        mc.cal(images)
        print mc.as_message()
    """

    is_mono = True  # TODO Could get rid of is_mono

    def __init__(self, *args, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "narrow_stereo/left"
        super(MonoCalibrator, self).__init__(*args, **kwargs)

    def cal(self, images):
        """
        Calibrate camera from given images
        """
        goodcorners = self.collect_corners(images)
        self.cal_fromcorners(goodcorners)
        self.calibrated = True

    def collect_corners(self, images):
        """
        :param images: source images containing chessboards
        :type images: list of :class:`cvMat`

        Find chessboards in all images.

        Return [ (corners, ids, ChessboardInfo) ]
        """
        self.size = (images[0].shape[1], images[0].shape[0])
        corners = [self.get_corners(i) for i in images]

        goodcorners = [(co, ids, b) for (ok, co, ids, b) in corners if ok]
        if not goodcorners:
            raise CalibrationException("No corners found in images!")
        return goodcorners

    def cal_fromcorners(self, good):
        """
        :param good: Good corner positions and boards
        :type good: [(corners, ChessboardInfo)]
        """

        (ipts, ids, boards) = zip(*good)
        opts = self.mk_object_points(boards)
        # If FIX_ASPECT_RATIO flag set, enforce focal lengths have 1/1 ratio
        intrinsics_in = numpy.eye(3, dtype=numpy.float64)

        if self.pattern == Patterns.ChArUco:
            if self.camera_model == CAMERA_MODEL.FISHEYE:
                raise NotImplemented(
                    "Can't perform fisheye calibration with ChArUco board"
                )

            (
                reproj_err,
                self.intrinsics,
                self.distortion,
                rvecs,
                tvecs,
            ) = cv2.aruco.calibrateCameraCharuco(
                ipts, ids, boards[0].charuco_board, self.size, intrinsics_in, None
            )

        elif self.camera_model == CAMERA_MODEL.PINHOLE:
            print("mono pinhole calibration...")
            (
                reproj_err,
                self.intrinsics,
                dist_coeffs,
                rvecs,
                tvecs,
            ) = cv2.calibrateCamera(
                opts, ipts, self.size, intrinsics_in, None, flags=self.calib_flags
            )
            # OpenCV returns more than 8 coefficients (the additional ones all zeros) when CALIB_RATIONAL_MODEL is set.
            # The extra ones include e.g. thin prism coefficients, which we are not interested in.
            self.distortion = dist_coeffs.flat[:8].reshape(-1, 1)

            # print results
            print("reproj_err = ", reproj_err)
            print("intrinsics = ", self.intrinsics)
            print("distortion = ", self.distortion)

        elif self.camera_model == CAMERA_MODEL.FISHEYE:
            print("mono fisheye calibration...")
            # WARNING: cv2.fisheye.calibrate wants float64 points
            ipts64 = numpy.asarray(ipts, dtype=numpy.float64)
            ipts = ipts64
            opts64 = numpy.asarray(opts, dtype=numpy.float64)
            opts = opts64
            (
                reproj_err,
                self.intrinsics,
                self.distortion,
                rvecs,
                tvecs,
            ) = cv2.fisheye.calibrate(
                opts,
                ipts,
                self.size,
                intrinsics_in,
                None,
                flags=self.fisheye_calib_flags,
            )

            # print results
            print("reproj_err = ", reproj_err)
            print("intrinsics = ", self.intrinsics)
            print("distortion = ", self.distortion)

        # R is identity matrix for monocular calibration
        self.R = numpy.eye(3, dtype=numpy.float64)
        self.P = numpy.zeros((3, 4), dtype=numpy.float64)

        self.set_alpha(0.0)

    def set_alpha(self, a):
        """
        Set the alpha value for the calibrated camera solution.  The alpha
        value is a zoom, and ranges from 0 (zoomed in, all pixels in
        calibrated image are valid) to 1 (zoomed out, all pixels in
        original image are in calibrated image).
        """

        if self.camera_model == CAMERA_MODEL.PINHOLE:
            # NOTE: Prior to Electric, this code was broken such that we never actually saved the new
            # camera matrix. In effect, this enforced P = [K|0] for monocular cameras.
            # TODO: Verify that OpenCV #1199 gets applied (improved GetOptimalNewCameraMatrix)
            ncm, _ = cv2.getOptimalNewCameraMatrix(
                self.intrinsics, self.distortion, self.size, a
            )
            for j in range(3):
                for i in range(3):
                    self.P[j, i] = ncm[j, i]
            self.mapx, self.mapy = cv2.initUndistortRectifyMap(
                self.intrinsics, self.distortion, self.R, ncm, self.size, cv2.CV_32FC1
            )
        elif self.camera_model == CAMERA_MODEL.FISHEYE:
            # NOTE: estimateNewCameraMatrixForUndistortRectify not producing proper results, using a naive approach instead:
            self.P[:3, :3] = self.intrinsics[:3, :3]
            self.P[0, 0] /= 1.0 + a
            self.P[1, 1] /= 1.0 + a
            self.mapx, self.mapy = cv2.fisheye.initUndistortRectifyMap(
                self.intrinsics,
                self.distortion,
                self.R,
                self.P,
                self.size,
                cv2.CV_32FC1,
            )

    def remap(self, src):
        """
        :param src: source image
        :type src: :class:`cvMat`

        Apply the post-calibration undistortion to the source image
        """
        return cv2.remap(src, self.mapx, self.mapy, cv2.INTER_LINEAR)

    def undistort_points(self, src):
        """
        :param src: N source pixel points (u,v) as an Nx2 matrix
        :type src: :class:`cvMat`

        Apply the post-calibration undistortion to the source points
        """
        if self.camera_model == CAMERA_MODEL.PINHOLE:
            return cv2.undistortPoints(
                src, self.intrinsics, self.distortion, R=self.R, P=self.P
            )
        elif self.camera_model == CAMERA_MODEL.FISHEYE:
            return cv2.fisheye.undistortPoints(
                src, self.intrinsics, self.distortion, R=self.R, P=self.P
            )

    def as_message(self):
        """Return the camera calibration as a CameraInfo message"""
        return self.lrmsg(
            self.distortion,
            self.intrinsics,
            self.R,
            self.P,
            self.size,
            self.camera_model,
        )

    def from_message(self, msg, alpha=0.0):
        """Initialize the camera calibration from a CameraInfo message"""

        self.size = (msg.width, msg.height)
        self.intrinsics = numpy.array(msg.K, dtype=numpy.float64, copy=True).reshape(
            (3, 3)
        )
        self.distortion = numpy.array(msg.D, dtype=numpy.float64, copy=True).reshape(
            (len(msg.D), 1)
        )
        self.R = numpy.array(msg.R, dtype=numpy.float64, copy=True).reshape((3, 3))
        self.P = numpy.array(msg.P, dtype=numpy.float64, copy=True).reshape((3, 4))

        self.set_alpha(0.0)

    def report(self):
        self.lrreport(self.distortion, self.intrinsics, self.R, self.P)

    def ost(self):
        return self.lrost(
            self.name, self.distortion, self.intrinsics, self.R, self.P, self.size
        )

    def yaml(self):
        return self.lryaml(
            self.name,
            self.distortion,
            self.intrinsics,
            self.R,
            self.P,
            self.size,
            self.camera_model,
        )

    def linear_error_from_image(self, image):
        """
        Detect the checkerboard and compute the linear error.
        Mainly for use in tests.
        """
        _, corners, _, ids, board, _ = self.downsample_and_detect(image)
        if corners is None:
            return None

        undistorted = self.undistort_points(corners)
        return self.linear_error(undistorted, ids, board)

    @staticmethod
    def linear_error(corners, ids, b):
        """
        Returns the linear error for a set of corners detected in the unrectified image.
        """

        if corners is None:
            return None

        corners = numpy.squeeze(corners)

        def pt2line(x0, y0, x1, y1, x2, y2):
            """point is (x0, y0), line is (x1, y1, x2, y2)"""
            return abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)) / math.sqrt(
                (x2 - x1) ** 2 + (y2 - y1) ** 2
            )

        n_cols = b.n_cols
        n_rows = b.n_rows
        if b.pattern == "charuco":
            n_cols -= 1
            n_rows -= 1
        n_pts = n_cols * n_rows

        if ids is None:
            ids = numpy.arange(n_pts).reshape((n_pts, 1))

        ids_to_idx = dict((ids[i, 0], i) for i in range(len(ids)))

        errors = []
        for row in range(n_rows):
            row_min = row * n_cols
            row_max = (row + 1) * n_cols
            pts_in_row = [x for x in ids if row_min <= x < row_max]

            # not enough points to calculate error
            if len(pts_in_row) <= 2:
                continue

            left_pt = min(pts_in_row)[0]
            right_pt = max(pts_in_row)[0]
            x_left = corners[ids_to_idx[left_pt], 0]
            y_left = corners[ids_to_idx[left_pt], 1]
            x_right = corners[ids_to_idx[right_pt], 0]
            y_right = corners[ids_to_idx[right_pt], 1]

            for pt in pts_in_row:
                if pt[0] in (left_pt, right_pt):
                    continue
                x = corners[ids_to_idx[pt[0]], 0]
                y = corners[ids_to_idx[pt[0]], 1]
                errors.append(pt2line(x, y, x_left, y_left, x_right, y_right))

        if errors:
            return math.sqrt(sum([e**2 for e in errors]) / len(errors))
        else:
            return None

    def do_calibration(self, dump=False):
        if not self.good_corners:
            print("**** Collecting corners for all images! ****")  # DEBUG
            images = [i for (p, i) in self.db]
            self.good_corners = self.collect_corners(images)
        self.size = (
            self.db[0][1].shape[1],
            self.db[0][1].shape[0],
        )  # TODO Needs to be set externally
        # Dump should only occur if user wants it
        if dump:
            pickle.dump(
                (self.is_mono, self.size, self.good_corners),
                open(
                    "/tmp/camera_calibration_%08x.pickle" % random.getrandbits(32), "w"
                ),
            )
        self.cal_fromcorners(self.good_corners)
        self.calibrated = True
        # DEBUG
        print((self.report()))
        print((self.ost()))

    def do_file_calibration(self, image_path_list):
        # exclude files that are not images
        image_path_list = [
            f for f in image_path_list if f.endswith(".png") or f.endswith(".jpg")
        ]
        self.raw_images = [cv2.imread(f) for f in image_path_list]

        self.cal(self.raw_images)

    def save_undistort_images(self, save_path):
        self.undistort_images = []
        # for image in self.raw_images:
        for i in range(len(self.raw_images)):
            # self.undistort_images.append(self.undistort(image))
            image = self.raw_images[i]
            # convert to gray
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            linear_error = -1

            # Get display-image-to-be (scrib) and detection of the calibration target
            (
                scrib_mono,
                corners,
                downsampled_corners,
                ids,
                board,
                (x_scale, y_scale),
            ) = self.downsample_and_detect(gray)

            if self.calibrated:
                # Show rectified image
                # TODO Pull out downsampling code into function
                gray_remap = self.remap(gray)
                gray_rect = gray_remap
                if x_scale != 1.0 or y_scale != 1.0:
                    gray_rect = cv2.resize(
                        gray_remap, (scrib_mono.shape[1], scrib_mono.shape[0])
                    )

                scrib = cv2.cvtColor(gray_rect, cv2.COLOR_GRAY2BGR)

                if corners is not None:
                    # Report linear error
                    undistorted = self.undistort_points(corners)
                    linear_error = self.linear_error(undistorted, ids, board)

                    # Draw rectified corners
                    scrib_src = undistorted.copy()
                    scrib_src[:, :, 0] /= x_scale
                    scrib_src[:, :, 1] /= y_scale
                    cv2.drawChessboardCorners(
                        scrib, (board.n_cols, board.n_rows), scrib_src, True
                    )
                    # save undistort image
                    self.undistort_images.append(scrib)

        # save undistort images
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        for i in track(range(len(self.undistort_images))):
            img_name = "undistort_" + str(i) + ".png"
            img_save_path = os.path.join(save_path, img_name)
            # make sure the save path exists
            cv2.imwrite(img_save_path, self.undistort_images[i])
