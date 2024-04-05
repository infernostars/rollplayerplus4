import colorsys
import discord


def normalize(min_val, max_val, value):
    """
    Linearly normalize a value between a minimum and maximum value to a number between 0 and 1.
    If the value is outside the min-max range, it will be clamped to the valid range.

    Args:
    min_val (float): The minimum valid value.
    max_val (float): The maximum valid value.
    value (float): The value to be normalized.

    Returns:
    float: The normalized value between 0 and 1.
    """
    if value < min_val:
        return 0.0
    elif value > max_val:
        return 1.0
    else:
        return (value - min_val) / (max_val - min_val)


def interpolate_color_hsv(value: float, min_value: float = 0.0, max_value: float = 1.0) -> discord.Color:
    """
    Interpolates a color between red (0.0) and green (1.0) in the HSV color space.
    The brightness (value) is kept constant throughout the interpolation.

    Parameters:
    value (float): The value to interpolate, between 0.0 and 1.0.
    min_value (float, optional): The minimum value, defaults to 0.0.
    max_value (float, optional): The maximum value, defaults to 1.0.

    Returns:
    discord.Color: The interpolated color as a Discord color.
    """
    # Clamp the value between the minimum and maximum
    value = max(min(value, max_value), min_value)

    # Map the value to the hue range (0 to 120 degrees)
    hue = value * 120.0

    # Use a constant saturation and value (brightness)
    saturation = 0.8
    brightness = 0.8

    # Convert the HSV color to RGB
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, saturation, brightness)

    # Convert the RGB values to a Discord color
    return discord.Color.from_rgb(int(r * 255), int(g * 255), int(b * 255))
