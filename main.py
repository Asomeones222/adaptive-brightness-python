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


def derive_current_luminance(interval=1):
    try:
        while True:
            # Generate a timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            # Take a screenshot using ImageGrab
            screenshot = ImageGrab.grab()
            print(f'Screenshot taken on {timestamp}')

            yield derive_luminance_from_img(screenshot)

            # Wait for the specified interval (1 second by default)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped watching luminance.")


def list_displays_brightness() -> None:
    # Initialize the WMI interface
    c: wmi.WMI = wmi.WMI(namespace='wmi')

    # Query all instances of WmiMonitorBrightness
    brightness_controls: List[wmi._wmi_object] = c.WmiMonitorBrightness()

    if not brightness_controls:
        print("No displays supporting software brightness control were found.")
        return

    for i, b in enumerate(brightness_controls, start=0):
        if not b.InstanceName:
            print(f"Display {i + 1} does not support software brightness control")
            continue

        print(f"Display {i + 1}: {b.InstanceName}")
        print("Set display's brightness to: ", end=" ")

        while True:
            user_brightness_input = input()
            if not user_brightness_input.isdigit() or int(user_brightness_input) > 100 \
                    or int(user_brightness_input) < 0:
                print("Please enter a value between 0 and 100 inclusive")
            else:
                break

        ith_display_methods = c.WmiMonitorBrightnessMethods()[i]
        ith_display_methods.WmiSetBrightness(int(user_brightness_input), i)


if __name__ == "__main__":
    print(next(derive_current_luminance(1)))
