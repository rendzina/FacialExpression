#!/usr/bin/env python3

# This is a demo of Xnor.ai's AI2GO platform, which provides
# fast, low-power AI on embedded processors.
#
# This is a Raspberry Pi application that reads data from the
# Pi camera, uses AI2GO's facial expression classifier to assess camera frames
# of people in the image, and shows a suitable image onscreen.
#
# For more details on setting this demo up and running it, see:
# http://www.digitalenvironment.org
#
# Based on Matt Welsh's AI2GO example at
# https://medium.com/@mdwdotla/true-ai-on-a-raspberry-pi-with-no-extra-hardware-dcdbff12d068
#
#  See README:
#  To uninstall existing xnor model:
#  python3 -m pip uninstall xnornet
#  To instal new xnor model:
#  python3 -m pip install xnornet*.whl
#  To run this code:
#  python3 facial_expression.py
#  To autostart this code on the Pi:
#  edit nano /home/pi/.config/autostart/facial_expression.desktop
#
import argparse
import datetime
import random
import sys
import time
import os.path
from itertools import cycle
#
import xnornet
from tkinter import *
from PIL import Image, ImageTk
import picamera
import common_util.ansi as ansi
import common_util.colors as colors

if sys.version_info[0] < 3:
    sys.exit("This app requires Python 3.")

# Draw canvas for 720x720 pixel Neopixel screen
canvas_width = 720
canvas_height =720
master = Tk()
canvas = Canvas(master, bg = "white",
      width = canvas_width, height = canvas_height)
canvas.pack()

# Set to True to generate fake data for testing.
FAKE_DATA = False

# Face image png file location
DIR_NAME='/home/pi/Public/faces'

# These constants are initialized below.
# Input resolution
INPUT_RES = 0
# Constant frame size
SINGLE_FRAME_SIZE_RGB = 0
SINGLE_FRAME_SIZE_YUV = 0
YUV420P_Y_PLANE_SIZE = 0
YUV420P_U_PLANE_SIZE = 0
YUV420P_V_PLANE_SIZE = 0

# Defines emotions used by emotion classifier
EMOTIONS = ['happy', 'sad', 'anger', 'fear', 'disgust', 'surprise', 'neutral']
BAD_MODEL_ERROR = (ansi.RED + "ERROR: " + ansi.NORMAL + "This app requires the "
   "facial-expression-classifier model to be installed.")

# Place facial exression images on canvas - add system halt for headless mode
def _imageAdd(face = 'unknown'):
    button = Button(master, width = 3, text = 'Halt', anchor='w',
                        fg = 'lightgray', command = shutdown, bg = "white")
    canvas.delete("all")
    try:
        if os.path.isfile(os.path.join(DIR_NAME,"face_" + face + ".png")):
            load = Image.open(DIR_NAME + "/face_" + face + ".png")
            faceImage = ImageTk.PhotoImage(load)
        else:
            load = Image.open(DIR_NAME + "/face_makeaface.png")
            faceImage = ImageTk.PhotoImage(load)
    except IOError:
        pass
    canvas.create_image(0, 0, anchor = 'nw', image = faceImage)
    button_window = canvas.create_window(10, 580, anchor='nw', window=button)
    master.update()


def shutdown():
    os.system("sudo shutdown -h now")


def _initialize_camera_vars(camera_res):
    """Initialize camera constants."""
    global INPUT_RES
    global SINGLE_FRAME_SIZE_RGB
    global SINGLE_FRAME_SIZE_YUV
    global YUV420P_Y_PLANE_SIZE
    global YUV420P_U_PLANE_SIZE
    global YUV420P_V_PLANE_SIZE
    #
    INPUT_RES = camera_res
    SINGLE_FRAME_SIZE_RGB = INPUT_RES[0] * INPUT_RES[1] * 3
    SINGLE_FRAME_SIZE_YUV = INPUT_RES[0] * INPUT_RES[1] * 3 // 2
    YUV420P_Y_PLANE_SIZE = INPUT_RES[0] * INPUT_RES[1]
    YUV420P_U_PLANE_SIZE = YUV420P_Y_PLANE_SIZE // 4
    YUV420P_V_PLANE_SIZE = YUV420P_U_PLANE_SIZE


def _make_argument_parser():
    """Create a command-line argument parser object."""
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--camera_frame_rate",
        action='store',
        type=int,
        default=8,
        help="Adjust the framerate of the camera.")
    parser.add_argument(
        "--camera_brightness",
        action='store',
        type=int,
        default=60,
        help="Adjust the brightness of the camera.")
    parser.add_argument(
        "--camera_recording_format",
        action='store',
        type=str,
        default='yuv',
        choices={'yuv', 'rgb'},
        help="Changing the camera recording format, \'yuv\' format is "
        "implicitly defaulted to YUV420P.")
    parser.add_argument(
        "--camera_input_resolution",
        action='store',
        nargs=2,
        type=int,
        default=(512, 512),
        help="Input Resolution of the camera.")
        #default=(512, 512),
    return parser


def _get_camera_frame(args, camera, stream):
    """Get a frame from the CircularIO buffer."""
    cam_output = stream.getvalue()

    if args.camera_recording_format == 'yuv':
        # The camera has not written anything to the CircularIO yet
        # Thus no frame is been captured
        if len(cam_output) != SINGLE_FRAME_SIZE_YUV:
            return None
        # Split YUV plane
        y_plane = cam_output[0:YUV420P_Y_PLANE_SIZE]
        u_plane = cam_output[YUV420P_Y_PLANE_SIZE:YUV420P_Y_PLANE_SIZE +
                             YUV420P_U_PLANE_SIZE]
        v_plane = cam_output[YUV420P_Y_PLANE_SIZE +
                             YUV420P_U_PLANE_SIZE:SINGLE_FRAME_SIZE_YUV]
        # Passing corresponding YUV plane
        model_input = xnornet.Input.yuv420p_image(INPUT_RES, y_plane, u_plane,
                                                  v_plane)
    elif args.camera_recording_format == 'rgb':
        # The camera has not written anything to the CircularIO yet
        # Thus no frame is been captured
        if len(cam_output) != SINGLE_FRAME_SIZE_RGB:
            return None
        model_input = xnornet.Input.rgb_image(INPUT_RES, cam_output)
    else:
        raise ValueError("Unsupported recording format")

    return model_input


def _inference_loop(args, camera, stream, model):
    """Main inference loop."""
    while True:
        model_input = _get_camera_frame(args, camera, stream)
        if model_input is not None:
            results = model.evaluate(model_input)
            print(results)
            if FAKE_DATA:
                expression = random.choice(EMOTIONS) # get random emotion
                _imageAdd(expression)
            else:
                face = ([element.label for element in results])
                if face:
                    expression = str(face[0])
                    # Example return: [ClassLabel(class_id=1825641713, label='neutral')]
                    #print("{}".format(expression))
                    _imageAdd(expression)
                else:
                    _imageAdd()
            time.sleep(2.0)


def main(args=None):
    parser = _make_argument_parser()
    args = parser.parse_args(args)

    try:
        camera = picamera.PiCamera()
        camera.resolution = tuple(args.camera_input_resolution)
        _initialize_camera_vars(camera.resolution)

        # Initialize the buffer for picamera to hold the frame
        # https://picamera.readthedocs.io/en/release-1.13/api_streams.html?highlight=PiCameraCircularIO
        if args.camera_recording_format == 'yuv':
            stream = picamera.PiCameraCircularIO(
                camera, size=SINGLE_FRAME_SIZE_YUV)
        elif args.camera_recording_format == 'rgb':
            stream = picamera.PiCameraCircularIO(
                camera, size=SINGLE_FRAME_SIZE_RGB)
        else:
            raise ValueError("Unsupported recording format")

        camera.framerate = args.camera_frame_rate
        camera.brightness = args.camera_brightness
        # Record to the internal CircularIO
        # PiCamera's YUV is YUV420P
        # https://picamera.readthedocs.io/en/release-1.13/recipes2.html#unencoded-image-capture-yuv-format
        camera.start_recording(stream, format=args.camera_recording_format)

        # Load Xnor model from disk.
        model = xnornet.Model.load_built_in()

        # Verify model is facial expression classification model
        for class_label in model.class_labels:
            if class_label not in EMOTIONS:
                sys.exit(BAD_MODEL_ERROR)

        _inference_loop(args, camera, stream, model)

    except Exception as e:
        raise e
    finally:
        # For good practice, kill it by ctrl+c anyway.
        camera.stop_recording()
        camera.close()


if __name__ == "__main__":
    main()
