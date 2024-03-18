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
    print(f'Screencapture taken on {timestamp}')
    return screencapture


def derive_current_luminance(interval: float = 1, sleep: bool = True):
    try:

        while True:
            yield derive_luminance_from_img(take_screencapture())

            # Wait for the specified interval (1 second by default)
            if sleep:
                time.sleep(interval)

    except InterruptedError | KeyboardInterrupt:
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
            f"Display {display_index} {display.InstanceName} does not support software brightness control\n {display}.")

    print(f"Display {display_index}: {display.InstanceName}")
    print(f"Set display's brightness to: {brightness}")

    display_methods = c.WmiMonitorBrightnessMethods()[display_index]
    display_methods.WmiSetBrightness(brightness, display_index)
    return display.CurrentBrightness


if __name__ == "__main__":
    previous_brightness = -100
    # The difference between previous and next brightness needed to set the new brightness
    # We use tolerance, so we don't send too many unnecessary commands to the display
    TOLERANCE = 5
    for luminance in derive_current_luminance(0.5):
        next_brightness = int(100 - luminance / 2)
        if abs(next_brightness - previous_brightness) > TOLERANCE:
            previous_brightness = set_displays_brightness(0, next_brightness)
