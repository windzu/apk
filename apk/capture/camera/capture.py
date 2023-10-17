"""
Author: windzu windzu1@gmail.com
Date: 2023-09-07 23:32:52
LastEditors: windzu windzu1@gmail.com
LastEditTime: 2023-09-08 01:47:44
Description: 
Copyright (c) 2023 by windzu, All Rights Reserved. 
"""
import os
import warnings
from multiprocessing import Process, Queue

import cv2
import gi
import numpy as np

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

# 忽略所有的"TypeError: can't convert return value to desired type"警告
warnings.filterwarnings(
    "ignore", "TypeError: can't convert return value to desired type"
)


class Capture:
    def __init__(
        self,
        enable_nv,
        device,
        width,
        height,
        fps,
        format,
        store_path,
    ):
        self.enable_nv = enable_nv
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.format = format
        self.store_path = store_path
        if self.store_path[0] == "~":
            self.store_path = os.path.expanduser(self.store_path)

        # init params
        self.store_count = 0
        self.img_queue = Queue(maxsize=20)
        self.gst_process = None
        self.display_process = None

        # init pipeline
        Gst.init(None)
        self.initialize_pipeline()

    def initialize_pipeline(self):
        if self.enable_nv:
            pipeline_str = (
                f"nvv4l2camerasrc device={self.device} ! video/x-raw(memory:NVMM),format={self.format}, "
                f"width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
                "nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink emit-signals=True"
            )
        else:
            pipeline_str = (
                f"v4l2src device={self.device} ! video/x-raw,format={self.format}, "
                f"width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
                "videoconvert ! video/x-raw,format=BGR ! appsink name=sink emit-signals=True"
            )
        self.pipeline = Gst.parse_launch(pipeline_str)
        self.sink = self.pipeline.get_by_name("sink")
        self.sink.connect("new-sample", self.on_buffer)

    def on_buffer(self, sink):
        sample = sink.emit("pull-sample")
        if sample is None:
            print("Failed to pull sample from sink")
            return Gst.FlowReturn.ERROR

        buf = sample.get_buffer()
        if buf is None:
            print("Sample contains no buffer")
            return Gst.FlowReturn.ERROR
        result, mapinfo = buf.map(Gst.MapFlags.READ)
        if not result:
            print("Buffer mapping failed")
            return Gst.FlowReturn.ERROR

        img_array = np.ndarray(
            (mapinfo.size,), dtype=np.uint8, buffer=mapinfo.data
        ).reshape((self.height, self.width, 3))

        self.img_queue.put(img_array)
        # mapinfo.unmap()
        buf.unmap(mapinfo)

        return Gst.FlowReturn.OK

    def capture(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        self.loop = GLib.MainLoop()

        bus.connect("message", self.on_message, self.loop)

        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            self.loop.run()
        except:
            pass
        self.pipeline.set_state(Gst.State.NULL)

    def on_message(self, bus, message, loop):
        mtype = message.type
        if mtype == Gst.MessageType.EOS:
            loop.quit()
        elif mtype == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, {debug}")
            loop.quit()

    def main_display(self):
        cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
        while True:
            if not self.img_queue.empty():
                img_array = self.img_queue.get()
                cv2.imshow("Preview", img_array)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    img_name = f"{self.store_count}.jpg"
                    img_path = os.path.join(self.store_path, img_name)
                    # make sure the store path exist
                    if not os.path.exists(self.store_path):
                        os.makedirs(self.store_path)
                    cv2.imwrite(img_path, img_array)
                    self.store_count += 1
                    print("Snapshot saved")
                    print("img_path:", img_path)

        cv2.destroyAllWindows()

    def cleanup(self):
        print("Cleaning up resources...")

        while not self.img_queue.empty():
            _ = self.img_queue.get()

        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)

        cv2.destroyAllWindows()

        if self.gst_process and self.gst_process.is_alive():
            self.gst_process.terminate()
            self.gst_process.join()

        if self.display_process and self.display_process.is_alive():
            self.display_process.terminate()
            self.display_process.join()

    def run(self):
        try:
            # 创建GStreamer进程
            self.gst_process = Process(target=self.capture)
            self.gst_process.start()

            # 创建OpenCV显示进程
            self.display_process = Process(target=self.main_display)
            self.display_process.start()

            # 等待两个进程完成
            self.gst_process.join()
            self.display_process.join()
        except KeyboardInterrupt:
            print("Interrupt received. Shutting down...")

        finally:
            self.cleanup()
