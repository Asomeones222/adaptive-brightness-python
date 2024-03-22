import argparse
import datetime
import time
from typing import List

import numpy as np
import wmi
from PIL import Image
from PIL import ImageGrab


def derive_luminance_from_img(img: Image) -> int:
    img = img.convert('RGB')  # Ensure image is in RGB format

    # Convert to a NumPy array
    img_data = np.array(img)

    # Derive Luminance from RGB
    # Luminance (perceived): (0.299*R + 0.587*G + 0.114*B)
    # Apply the formula to calculate luminance
    luminance = 0.299 * img_data[:, :, 0] + 0.587 * img_data[:, :, 1] + 0.114 * img_data[:, :, 2]
    return int(np.sum(luminance) / (img.height * img.width) / 255.0 * 100)


def take_screencapture():
    # Generate a timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Take a screenshot using ImageGrab
    screencapture = ImageGrab.grab()
    # print(f'Screencapture taken on {timestamp}')
    return screencapture


def derive_current_luminance(interval: float = 1, sleep: bool = True):
    try:

        while True:
            yield derive_luminance_from_img(take_screencapture())

            # Wait for the specified interval (1 second by default)
            if sleep:
                time.sleep(interval)

    except KeyboardInterrupt:
        print("Stopped watching luminance.")


def set_displays_brightness(display_index: int, brightness: int):
    # Initialize the WMI interface
    c: wmi.WMI = wmi.WMI(namespace='wmi')

    # Query all instances of WmiMonitorBrightness
    brightness_controls: List[wmi._wmi_object] = c.WmiMonitorBrightness()
    if not brightness_controls:
        raise Exception("No displays supporting software brightness control were found.")

    display = brightness_controls[display_index]
    if not display.InstanceName:
        raise Exception(
            f"Display {display_index} {display.InstanceName} does not support software brightness control.")

    print(f"Display {display_index}: {display.InstanceName}")
    print(f"Set display's brightness to {brightness}")

    display_methods = c.WmiMonitorBrightnessMethods()[display_index]
    display_methods.WmiSetBrightness(brightness, display_index)
    return display.CurrentBrightness


def is_valid_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Adaptive brightness',
        description='Sets brightness based on the luminance of the currently displayed content',
        epilog="""
        -t      Tolerance: The difference between previous and next brightness needed to set new brightness. Default = 5, minimum = 5.
        -max    Max brightness. Default = 100
        -min    Min brightness. Default = 0
        -i      Interval duration (seconds): Wait time before calling next luminance calculation. Default = 0.5, min = 0.1 .
        """)
    parser.add_argument('-t')
    parser.add_argument('-max')
    parser.add_argument('-min')
    parser.add_argument('-i')
    args = parser.parse_args()

    TOLERANCE = 5
    if args.t.isdigit() and int(args.t) >= 5:
        TOLERANCE = int(args.t)
    else:
        raise Exception("tolerance was not set, invalid value was passed")

    MAX_BRIGHTNESS = 100
    if args.max.isdigit() and int(args.max) <= 100:
        MAX_BRIGHTNESS = int(args.max)
    else:
        raise Exception("max brightness was not set, invalid value was passed")

    MIN_BRIGHTNESS = 0
    if args.min.isdigit() and int(args.min) >= 0:
        MIN_BRIGHTNESS = int(args.min)
    else:
        raise Exception("min brightness was not set, invalid value was passed")

    INTERVAL = 0.5
    if is_valid_float(args.i) and float(args.i) >= 0.1:
        INTERVAL = float(args.i)
    else:
        raise Exception("interval was not set, invalid value was passed")

    print("tolerance:", TOLERANCE)
    print("max brightness:", MAX_BRIGHTNESS)
    print("min brightness:", MIN_BRIGHTNESS)
    print("interval:", INTERVAL)

    previous_brightness = -100
    for luminance in derive_current_luminance(INTERVAL):
        next_brightness = int(100 - luminance / 2)
        if abs(next_brightness - previous_brightness) > TOLERANCE:
            previous_brightness = \
                set_displays_brightness(0, max(min(next_brightness, MAX_BRIGHTNESS), MIN_BRIGHTNESS))
