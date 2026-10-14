"""Resize supplied OUC reference PNGs without redrawing their logos.

Run with Python 3 and Pillow. All outputs go to the project's assets directory.
"""
from collections import Counter
from pathlib import Path
from PIL import Image

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def reference(name):
    image = Image.open(ASSETS / name).convert("RGBA")
    return image.crop(image.getchannel("A").getbbox())


def foreground(image, color):
    result = Image.new("RGBA", image.size, color + (0,))
    result.putalpha(image.getchannel("A"))
    return result


def fit(image, width, height):
    scale = min(width / image.width, height / image.height)
    return image.resize((round(image.width * scale), round(image.height * scale)),
                        Image.Resampling.LANCZOS)


def main():
    blue_reference = reference("reference_logo_RGB.png")
    counts = Counter()
    for count, pixel in blue_reference.getcolors(blue_reference.width * blue_reference.height):
        if pixel[3] == 255:
            counts[pixel[:3]] += count
    blue = counts.most_common(1)[0][0]
    white = (255, 255, 255)

    # Match the old wordmark's center and maximum extent; preserve proportions.
    for name, source, ink, paper in [
        ("background.png", "reference_background_negative.png", white, blue),
        ("background_negative.png", "reference_background.png", blue, white),
    ]:
        mark = fit(foreground(reference(source), ink), 1171, 392)
        canvas = Image.new("RGBA", (2960, 2160), paper + (255,))
        canvas.alpha_composite(mark, (round(1230.5 - mark.width / 2),
                                      round(1865 - mark.height / 2)))
        canvas.convert("RGB").save(ASSETS / name, dpi=(300, 300))

    # Match each output name to its corresponding reference logo.
    for name, source, ink, paper in [
        ("logo_RGB.png", "reference_logo_RGB.png", blue, white),
        ("logo_RGB_negative.png", "reference_logo_RGB_negative.png", white, blue),
    ]:
        mark = fit(foreground(reference(source), ink), 954, 954)
        canvas = Image.new("RGBA", (1865, 2220), paper + (255,))
        canvas.alpha_composite(mark, (round(929 - mark.width / 2),
                                      round(1200 - mark.height / 2)))
        canvas = canvas.convert("RGB")
        canvas.save(ASSETS / name, dpi=(72, 72))
    print(f"OUC blue: RGB{blue}; four PNGs written to {ASSETS}")


if __name__ == "__main__":
    main()
