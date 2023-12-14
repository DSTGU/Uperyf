import cv2
import tkinter as tk
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk

class CameraApp:
    def __init__(self, root, available_cameras):
        self.root = root
        self.root.title("Camera Selector")

        self.available_cameras = available_cameras

        # Left Frame (for video feed)
        self.left_frame = ttk.Frame(root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10)
        self.video_label = ttk.Label(self.left_frame, text="Camera Feed:")
        self.video_label.pack(pady=10)
        self.video_frame = ttk.Frame(self.left_frame, width=600, height=400)
        self.video_frame.pack()

        # Right Frame (for utility controls)
        self.right_frame = ttk.Frame(root)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)

        self.camera_label = ttk.Label(self.right_frame, text="Select Camera:")
        self.camera_label.grid(row=0, column=0, pady=5)
        self.camera_combobox = ttk.Combobox(self.right_frame, values=available_cameras)
        self.camera_combobox.grid(row=1, column=0, pady=5)

        self.select_button = ttk.Button(self.right_frame, text="Select Camera", command=self.select_camera)
        self.select_button.grid(row=2, column=0, pady=10)

        self.saturation_label = ttk.Label(self.right_frame, text="Saturation:")
        self.saturation_label.grid(row=3, column=0, pady=5)
        self.saturation_scale = ttk.Scale(self.right_frame, from_=0, to=2, orient=tk.HORIZONTAL,
                                          command=self.update_parameters)
        self.saturation_scale.set(1.0)
        self.saturation_scale.grid(row=4, column=0, pady=5)

        self.brightness_label = ttk.Label(self.right_frame, text="Brightness:")
        self.brightness_label.grid(row=5, column=0, pady=5)
        self.brightness_scale = ttk.Scale(self.right_frame, from_=0, to=2, orient=tk.HORIZONTAL,
                                          command=self.update_parameters)
        self.brightness_scale.set(1.0)
        self.brightness_scale.grid(row=6, column=0, pady=5)

        self.contrast_label = ttk.Label(self.right_frame, text="Contrast:")
        self.contrast_label.grid(row=7, column=0, pady=5)
        self.contrast_scale = ttk.Scale(self.right_frame, from_=-100, to=100, orient=tk.HORIZONTAL,
                                        command=self.update_parameters)
        self.contrast_scale.set(0)
        self.contrast_scale.grid(row=8, column=0, pady=5)

        self.select_button = ttk.Button(self.right_frame, text="Capture frame", command=self.capture_frame)
        self.select_button.grid(row=9, column=0, pady=10)

        self.video_capture = None
        self.selected_camera = None

        self.saturation_value = 1.0
        self.brightness_value = 1.0
        self.contrast_value = 0


    def select_camera(self):
        selected_camera = int(self.camera_combobox.get())

        if self.video_capture is not None:
            self.video_capture.release()

        self.video_capture = cv2.VideoCapture(selected_camera)

        if not self.video_capture.isOpened():
            print("Error opening the camera.")
            return

        self.selected_camera = selected_camera
        self.display_video()

    def update_parameters(self, _):
        self.saturation_value = self.saturation_scale.get()
        self.brightness_value = self.brightness_scale.get()
        self.contrast_value = self.contrast_scale.get()

    def display_video(self):
        _, frame = self.video_capture.read()

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype("float32")

            # Apply image processing based on slider values
            # Saturation
            (h, s, v) = cv2.split(frame)
            s = s * self.saturation_value
            s = np.clip(s, 0, 255)
            frame = cv2.merge([h, s, v])

            # Brightness
            frame = cv2.convertScaleAbs(frame, alpha=self.brightness_value, beta=0)
            # Contrast
            frame = cv2.convertScaleAbs(frame, alpha=1 + self.contrast_value / 100.0, beta=0)
            frame = cv2.cvtColor(frame, cv2.COLOR_HSV2RGB).astype("uint8")

            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=img)
            label = ttk.Label(self.video_frame, image=img)
            label.img = img
            label.grid(row=0, column=0)

        self.root.after(10, self.display_video)

    def capture_frame(self):
        if self.video_capture is not None and self.selected_camera is not None:
            ret, frame = self.video_capture.read()

            if ret:
                filename = f"captured_frame_camera_{self.selected_camera}.png"
                # Apply image processing based on slider values
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype("float32")
                # Apply image processing based on slider values
                # Saturation
                (h, s, v) = cv2.split(frame)
                s = s * self.saturation_value
                s = np.clip(s, 0, 255)
                frame = cv2.merge([h, s, v])

                # Brightness
                frame = cv2.convertScaleAbs(frame, alpha=self.brightness_value, beta=0)
                # Contrast
                frame = cv2.convertScaleAbs(frame, alpha=1 + self.contrast_value / 100.0, beta=0)
                frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR).astype("uint8")

                cv2.imwrite(filename, frame)
                print(f"Frame captured and saved as {filename}")
            else:
                print("Error capturing frame.")

    def run(self):
        self.root.mainloop()

def scan_for_cameras():
    # Start with camera index 0
    camera_index = 0
    available_cameras = []

    while True:
        # Try to open the camera
        cap = cv2.VideoCapture(camera_index)

        # Check if the camera is opened successfully
        if not cap.isOpened():
            break

        # Release the camera capture object
        cap.release()

        # Add the camera index to the list of available cameras
        available_cameras.append(camera_index)

        # Move to the next camera index
        camera_index += 1

    return available_cameras

if __name__ == "__main__":
    # Scan for available cameras
    cameras = scan_for_cameras()

    if not cameras:
        print("No cameras found.")
    else:
        root = tk.Tk()
        app = CameraApp(root, cameras)
        app.run()