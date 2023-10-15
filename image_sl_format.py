import random
import time
from PIL import Image
import pyperclip
import flet as ft
import os


class Formatter:
    def __init__(self):
        self.file_path: str = ""
        self.alpha_channel: bool = False
        self.size_limit: float = 50
        self.output: str = ""
        self.color_limit: int = 0
        self.base64_img: str = ""
        self.can_format: bool = False
        self.size_multiplier: int = 0
        self.width = None
        self.height = None
        self.current_file_name = ""

    def rgb_to_hex(self, rgb) -> str:
        if self.alpha_channel:
            out = "#{:02X}{:02X}{:02X}{:02X}".format(*rgb)
            return out
        else:
            out = "#{0:02x}{1:02x}{2:02x}".format(rgb[0], rgb[1], rgb[2])
            return out

    def format_image(self) -> bool:
        image = Image.open(self.file_path)
        width, height = image.size
        if width >= height:
            self.size_multiplier = int(self.size_limit) / width
        else:
            self.size_multiplier = int(self.size_limit) / height

        width, height = int(round(width*self.size_multiplier, 1)), int(round(height*self.size_multiplier, 1))
        self.width = width
        self.height = height

        if width < 1 or height < 1:
            return False

        image = image.resize((width, height))
        image = image.convert("P", colors=self.color_limit)
        image = image.convert('RGBA') if self.alpha_channel else image.convert('RGB')

        self.current_file_name = random.randint(111111111, 999999999)
        print(f"działa? | {self.current_file_name}.png")
        image.save(f"C:/SCPSL IMG FORMATTER/{self.current_file_name}.png")

        last_hex: str = ""
        output: str = "<size=5><line-height=84%>"

        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                hex_value = self.rgb_to_hex(pixel)

                if not last_hex == hex_value:
                    output += f"<color={hex_value}>█"

                elif last_hex == hex_value:
                    output += "█"

                last_hex = hex_value

            output += r"\n"

        self.output = output
        return True

    def main(self, page: ft.Page) -> None:
        page.visible = False
        page.title = "Image to SCP:SL hint formatter by @elektryk_andrzej"
        page.window_width = 700
        page.window_height = 700
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.window_opacity = 0.99
        page.window_center()
        page.window_min_width = 700
        page.window_max_width = 700
        page.window_max_height = 700
        page.window_min_height = 700
        page.window_maximizable = False
        page.update()

        def format_button_clicked(e):
            if not self.can_format:
                page.update()
                return

            if transparency.value == "✔ True":
                self.alpha_channel = True
            else:
                self.alpha_channel = False
            self.size_limit = pix_count.value

            try:
                if int(self.size_limit) > 200:
                    pix_count.border_color = ft.colors.RED
                    pix_count.update()
                    return
                else:
                    pix_count.border_color = ft.colors.BLACK
                    pix_count.update()
            except:
                pix_count.border_color = ft.colors.RED
                pix_count.update()
                return

            try:
                self.color_limit = int(colors.value)
                if int(self.color_limit) > 256:
                    colors.border_color = ft.colors.RED
                    colors.update()
                    return
                else:
                    colors.border_color = ft.colors.BLACK
                    colors.update()
            except:
                colors.border_color = ft.colors.RED
                colors.update()
                return

            self.format_image()
            output_img.src = f"C:/SCPSL IMG FORMATTER/{self.current_file_name}.png"
            output_img.visible = True
            arrow_right.visible = True
            page.update()
            time.sleep(0.2)
            output_text.value = \
                "Image has been formatted\n"\
                f"(size - {len(self.output)} characters)"
            show_info(e)

        def changed_file_path(e):
            if os.path.isfile(file_path.value):
                self.can_format = True
                selected_img.src = file_path.value
                format_button.text = "Format!"
                self.file_path = file_path.value
            else:
                format_button.text = "Invalid image path"
                selected_img.src = "None"
                arrow_right.visible = False
                output_img.visible = False
                output_img.src = "None"

            page.update()

        def delete_previevs(e):
            folder = "C:/SCPSL IMG FORMATTER/"
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        os.remove(file_path)
                except:
                    return

        def copy_to_clipboard(e):
            pyperclip.copy(self.output)
            info_popup.open = False
            info_popup.update()

        def show_info(e):
            info_popup.open = True
            info_popup.update()

        output_text = ft.Text(
            value="",
            size=20
        )

        info_popup = ft.BottomSheet(
            ft.Container(
                ft.Row(
                    [
                        output_text,
                        ft.FilledButton("Copy to clipboard",
                                        on_click=copy_to_clipboard,
                                        width=200, height=50,
                                        icon=ft.icons.COPY)
                    ],
                    tight=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=30,
                width=700
            ),
            open=True
        )
        page.overlay.append(info_popup)

        no_img_selected = ft.Icon(
            name=ft.icons.IMAGE_SEARCH,
            size=250,
        )

        selected_img = ft.Image(
            width=250,
            height=250,
            fit=ft.ImageFit.CONTAIN,
            src="None",
            error_content=no_img_selected,

        )

        output_img = ft.Image(
            width=250,
            height=250,
            fit=ft.ImageFit.CONTAIN,
            src="None",
            error_content=no_img_selected,
            visible=False,
            tooltip="In-game image will look similar to this"
        )

        file_path = ft.TextField(
            label="Image path",
            prefix_icon=ft.icons.IMAGE,
            on_change=changed_file_path,
            width=545,
            hint_text="e.g. boykisser.jpg"
        )

        transparency = ft.Dropdown(
            label="Transparency",
            options=[
                ft.dropdown.Option("✔ True"),
                ft.dropdown.Option("❌ False"),
            ],
            prefix_icon=ft.icons.REMOVE_RED_EYE,
            width=175
        )

        pix_count = ft.TextField(
            label="Pixel count",
            prefix_icon=ft.icons.IMAGE_ASPECT_RATIO,
            width=175
        )

        format_button = ft.ElevatedButton(
            text="No image path provided...",
            icon=ft.icons.IMAGE_SEARCH_SHARP,
            on_click=format_button_clicked
        )

        colors = ft.TextField(
            label="Color count",
            width=175,
            prefix_icon=ft.icons.COLOR_LENS
        )

        arrow_right = ft.Icon(
            name=ft.icons.ARROW_RIGHT,
            size=50,
            visible=False
        )

        delete_previevs = ft.ElevatedButton(
            text="Delete old previevs",
            tooltip="Image previevs are saved on your computer",
            on_click=delete_previevs,
            icon=ft.icons.DELETE
        )

        faq = ft.Text(
            value="""
            How to get my image path?
                Shift + RMB on your image, and click "Copy As Path" 
                (remember to delete the quotation marks)
            
            I'm getting network errors when I add the image!
                Hints have a character limit, so if you get a network
                error, try lowering the number of pixels and colors.
            """
        )

        page.add(
            ft.Row(
                [file_path],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        page.add(
            ft.Row(
                [transparency, pix_count, colors],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        page.add(
            ft.Row(
                [selected_img, arrow_right, output_img],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        page.add(
            ft.Row(
                [format_button, delete_previevs],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        page.add(faq)
        page.update()
        page.visible = True


if __name__ == "__main__":
    formatter = Formatter()
    ft.app(target=formatter.main)
