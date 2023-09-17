import sys
from PIL import Image
import pyperclip
import time


class Formatter:
    def __init__(self,
                 file_path: str,
                 alpha_channel: bool,
                 size_limit: float,
                 color_limit: int):

        self.file_path: str = file_path
        self.alpha_channel: bool = alpha_channel
        self.size_limit: float = size_limit
        self.output: str or None = None
        self.color_limit = color_limit

    def format_image(self, pix_count):
        def rgb_to_hex(rgb):
            if self.alpha_channel:
                out = "#{:02X}{:02X}{:02X}{:02X}".format(*rgb)
                return out
            else:
                out = "#{0:02x}{1:02x}{2:02x}".format(rgb[0], rgb[1], rgb[2])
                return out

        image = Image.open(self.file_path)
        width, height = image.size
        width, height = int(round(width*pix_count, 1)), int(round(height*pix_count, 1))

        if width < 1 or height < 1:
            return "something got fucked up real bad if you see this"

        image = image.resize((width, height))
        image = image.convert('P', palette=Image.ADAPTIVE, colors=self.color_limit)
        image = image.convert('RGBA') if self.alpha_channel else image.convert('RGB')

        last_hex: str = ""
        output: str = "<size=5><line-height=84%>"

        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                hex_value = rgb_to_hex(pixel)

                if not last_hex == hex_value:
                    output += f"<color={hex_value}>█"

                elif last_hex == hex_value:
                    output += "█"

                last_hex = hex_value

            output += r"\n"

        return output

    def check_image(self, pixel_quality):
        if not sys.getsizeof(output := self.format_image(pixel_quality)) > self.size_limit:
            return output
        else:
            return None


if __name__ == "__main__":
    try:
        def input_handler(message: str, input_type: type, *, default):
            while True:
                answer = input(f"{message}\n->")

                if not answer:
                    if default is None:
                        continue
                    return default

                if input_type == bool:
                    if answer.casefold() == "false":
                        return False
                    elif answer.casefold() == "true":
                        return True
                    else:
                        print(f"Wrong type! Expected {input_type}")
                        continue

                try:
                    return input_type(answer)
                except:
                    print(f"Wrong type! Expected {input_type}")
                    continue

        file_path = input_handler("File path", str,
                                  default=None)

        alpha_channel = input_handler("Should image support transparency? - default: False", bool,
                                      default=False)

        size_limit = input_handler("How big can the file be? - default: 100kB", float,
                                   default=100000)

        color_limit = input_handler("How much colors should there be? - default: 96", int,
                                    default=96)

        pixel_quality: float = .01
        formatter = Formatter(file_path, alpha_channel, size_limit, color_limit)
        last_output: str = ""
        while True:
            pixel_quality += pixel_quality * .02

            output: str or None = formatter.check_image(pixel_quality)

            if output:
                last_output = output
                continue

            pyperclip.copy(last_output)
            print("Formatted! Your image has been copied to the clipboard."
                  "\nProgram will automatically restart in 5 seconds.")
            time.sleep(5)
            sys.exit()
    except Exception as e:
        print("Something went wrong -", e,
              "\nProgram will automatically restart in 5 seconds.")
        time.sleep(5)
        sys.exit()



