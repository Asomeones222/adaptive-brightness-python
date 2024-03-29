# Adaptive Brightness Program - Windows

This Python program automatically adjusts the brightness of your display based on the luminance of the content currently
being displayed on the screen.

## Features

- **Dynamic Brightness Adjustment**: Automatically adjusts the brightness based on the content's luminance.
- **Customizable Parameters**: Users can set minimum and maximum brightness levels, the tolerance for brightness
  adjustment, and the interval between adjustments.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- Pillow Library: `pip install Pillow`
- Numpy Library: `pip install numpy`
- WMI Library (Windows only): `pip install WMI`

## Usage

To use the Adaptive Brightness Program, follow these steps:

1. Clone this repository or download the `main.py` file to your local machine.
2. Open a terminal or command prompt.
3. Navigate to the directory where `main.py` is located.
4. Run the program using Python with optional arguments to customize its behavior. For example:

```bash
python main.py -t 5 -max 100 -min 0 -i 0.2
```

### Command Line Arguments

- `-t`: Tolerance level for brightness adjustment (default = 5). This is the minimum difference between the current and
  the next brightness level required to trigger an adjustment.
- `-max`: Maximum brightness level (default = 100).
- `-min`: Minimum brightness level (default = 0).
- `-i`: Interval in seconds between each brightness check (default = 0.2).

## How It Works

The program captures the current screen content, calculates its average luminance, and adjusts the display's brightness
based on this luminance. It runs continuously until manually stopped, checking the screen at regular intervals defined
by the user.

## Contributing

Contributions to improve Adaptive Brightness Program are welcome. Feel free to fork the repository and submit pull
requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Finally

Free Palestine 🇵🇸♥