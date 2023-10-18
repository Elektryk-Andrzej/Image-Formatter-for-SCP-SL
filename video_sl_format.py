import cv2
from PIL import Image
import pyperclip

video_path = 'vid/whyyyyyy.mov'
pix_count = 60
all_output: str = ""z


def rgb_to_hex(rgb):
    return "#{0:02x}{1:02x}{2:02x}".format(rgb[0], rgb[1], rgb[2])


cap = cv2.VideoCapture(video_path)
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frames: list = []
frame_number = 0
last_hex = ""

while True:
    frame_number += 1

    output: str = "<line-height=87%>"
    ret, frame = cap.read()

    if not ret:
        break

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    image = image.resize((pix_count, pix_count))
    width, height = image.size

    for y in range(height):
        for x in range(width):
            pixel = image.getpixel((x, y))
            hex_value = rgb_to_hex(pixel)
            if not last_hex == hex_value:
                output += f"<color={hex_value}>█"
            else:
                output += "█"
            last_hex = hex_value
        output += r"\n"
    output += r"\n\n\n\n\n\n\n\n\n"

    frames.append(output)

for i, v in enumerate(frames):
    all_output += f"SAVE {{FR{i}}} {v}\n"


for i, v in enumerate(frames):
    all_output += f"HINT 1 {{FR{i}}}\nWAITSEC 0.5\n"

pyperclip.copy(all_output)

cap.release()