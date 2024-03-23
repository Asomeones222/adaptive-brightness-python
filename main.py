import argparse
import math
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
    screencapture = ImageGrab.grab()
    # timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # print(f'Screencapture taken on {timestamp}')
    return screencapture


def derive_current_luminance(interval: float = 1):
    try:
        while True:
            yield derive_luminance_from_img(take_screencapture())
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


def validate_arg(a, d, min, max):
    if a:
        if is_valid_float(a) and min <= float(a) <= max:
            return float(a)
        else:
            raise Exception(f"Argument was not set or an invalid value was passed: {a}")
    else:
        return d


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Adaptive brightness',
        description='Sets brightness based on the luminance of the currently displayed content',
        epilog="""
        -t      Tolerance: The difference between previous and next brightness needed to set new brightness. Default = 5, minimum = 5.
        -max    Max brightness. Default = 100
        -min    Min brightness. Default = 0
        -i      Interval duration (seconds): Wait time before calling next luminance calculation. Default = 0.2, min = 0.01 .
        """)
    parser.add_argument('-t')
    parser.add_argument('-max')
    parser.add_argument('-min')
    parser.add_argument('-i')
    args = parser.parse_args()

    TOLERANCE = int(validate_arg(args.t, d=5, min=5, max=100))
    MAX_BRIGHTNESS = int(validate_arg(args.max, d=100, min=0, max=100))
    MIN_BRIGHTNESS = int(validate_arg(args.min, d=0, min=0, max=100))
    INTERVAL = validate_arg(args.i, d=0.2, min=0.01, max=math.inf)

    print("tolerance:", TOLERANCE)
    print("max brightness:", MAX_BRIGHTNESS)
    print("min brightness:", MIN_BRIGHTNESS)
    print("interval:", INTERVAL)

    previous_brightness = 0
    for luminance in derive_current_luminance(INTERVAL):
        next_brightness = int(MAX_BRIGHTNESS - luminance / 2)
        if abs(next_brightness - previous_brightness) > TOLERANCE:
            previous_brightness = \
                set_displays_brightness(0, max(min(next_brightness, MAX_BRIGHTNESS), MIN_BRIGHTNESS))
