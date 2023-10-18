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
        self.can_format: bool = False
        self.size_multiplier: int = 0
        self.output_path: str = "C:/SCPSL IMG FORMATTER/output.png"

    def rgb_to_hex(self, rgb) -> str:
        if self.alpha_channel:
            out = "#{:02X}{:02X}{:02X}{:02X}".format(*rgb)
            return out
        else:
            out = "#{0:02x}{1:02x}{2:02x}".format(rgb[0], rgb[1], rgb[2])
            return out

    def format_image(self) -> None:
        image = Image.open(self.file_path)
        width, height = image.size
        if width >= height:
            self.size_multiplier = int(self.size_limit) / width
        else:
            self.size_multiplier = int(self.size_limit) / height

        width, height = int(round(width*self.size_multiplier, 1)), int(round(height*self.size_multiplier, 1))

        image = image.resize((width, height))
        image = image.convert("P", colors=self.color_limit, palette=Image.ADAPTIVE)
        image = image.convert('RGBA') if self.alpha_channel else image.convert('RGB')

        folder = 'C:/SCPSL IMG FORMATTER/'
        for filename in os.listdir(folder):
            os.remove(os.path.join(folder, filename))

        self.output_path = f"C:/SCPSL IMG FORMATTER/{str(random.randint(1111111111, 9999999999))}.png"

        image.save(self.output_path)

        last_hex: str = ""
        self.output: str = "<size=5><line-height=84%>"

        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                hex_value = self.rgb_to_hex(pixel)

                if not last_hex == hex_value:
                    self.output += f"<color={hex_value}>█"

                elif last_hex == hex_value:
                    self.output += "█"

                last_hex = hex_value

            self.output += r"\n"

    def main(self, page: ft.Page) -> None:
        page.visible = False
        page.title = "Image to SCP:SL hint formatter by @elektryk_andrzej"
        page.window_resizable = False
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        #page.window_opacity = 0.95
        page.window_center()
        page.window_width = 700
        page.window_height = 675
        page.window_maximizable = False
        page.theme_mode = "light"
        page.update()
        page.padding = 10
        page.bgcolor = "#00000000"
        page.window_bgcolor = "#00000000"

        def format_button_clicked(e):
            if not self.can_format:
                page.update()
                return

            if transparency.value == "✔ Yes":
                self.alpha_channel = True
            else:
                self.alpha_channel = False
            self.size_limit = pix_count.value

            try:
                if int(self.size_limit) > 100:
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
            output_img.visible = True
            output_img.src = self.output_path
            arrow_right.visible = True
            page.update()
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
                selected_img.src = "vanish"
                arrow_right.visible = False
                output_img.visible = False

            page.update()

        def copy_to_clipboard(e):
            pyperclip.copy(self.output)
            info_popup.open = False
            info_popup.update()

        def show_info(e):
            info_popup.open = True
            info_popup.update()

        output_text = ft.Text(
            value="",
            size=25,
            color="#ffffff"
        )

        info_popup = ft.BottomSheet(
            ft.Container(
                ft.Row(
                    [
                        output_text,

                        ft.FilledButton("Copy to clipboard",
                                        on_click=copy_to_clipboard,
                                        width=200, height=50,
                                        icon=ft.icons.COPY,
                                        style=ft.ButtonStyle(
                                            bgcolor={
                                                ft.MaterialState.HOVERED: "#ffffff"
                                            }
                                        ))
                    ],
                    tight=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=30,
                width=700,
                border_radius=ft.border_radius.vertical(10, 0),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["#222222", "#111111"],
                ),
            ),
            open=True,



        )

        page.overlay.append(info_popup)

        no_img_selected = ft.Icon(
            name=ft.icons.IMAGE_SEARCH,
            size=250,
            visible=False
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
            src=self.output_path,
            error_content=no_img_selected,
            visible=False,
            tooltip="In-game image will look similar to this"
        )

        file_path = ft.TextField(
            label="Image path",
            prefix_icon=ft.icons.IMAGE,
            on_change=changed_file_path,
            width=545,
            hint_text="e.g. boykisser.jpg",
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700
            )
        )

        transparency = ft.Dropdown(
            label="Transparency",
            value="❌ No",
            options=[
                ft.dropdown.Option("✔ Yes"),
                ft.dropdown.Option("❌ No"),
            ],
            prefix_icon=ft.icons.REMOVE_RED_EYE,
            width=175,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700,
                color="#000000"
            )
        )

        pix_count = ft.TextField(
            label="Pixel count",
            value=str(21),
            prefix_icon=ft.icons.IMAGE_ASPECT_RATIO,
            width=175,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700
            )
        )

        format_button = ft.ElevatedButton(
            text="No image path provided...",
            color="#ffffff",
            bgcolor="#00000000",
            icon=ft.icons.IMAGE_SEARCH_SHARP,
            on_click=format_button_clicked,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.MaterialState.DEFAULT: "#333333"
                },
                color={
                    ft.MaterialState.DEFAULT: "#000000"
                }
            ),
        )

        colors = ft.TextField(
            label="Color count",
            width=175,
            value=str(37),
            prefix_icon=ft.icons.COLOR_LENS,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700
            )
        )

        arrow_right = ft.Icon(
            name=ft.icons.ARROW_RIGHT,
            size=50,
            visible=False
        )

        ui = (ft.Container(
            ft.Stack([
                ft.Column([
                    ft.Row(
                        [file_path],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),

                    ft.Row(
                        [transparency, pix_count, colors],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),

                    ft.Row(
                        [selected_img, arrow_right, output_img],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),

                    ft.Row(
                        [format_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),

                    ft.Row(
                        [
                            ft.TextField(
                                value=
                                "How do I get a path of my image?\n\n"
                                "Have your image and this application in the same place (e.g. desktop) "
                                "and enter the file name (e.g. sus.jpg)."
                                ,
                                width=300,
                                height=130,
                                disabled=True,
                                text_size=12,
                                multiline=True,
                                color="#ffffff",
                            ),

                            ft.TextField(
                                value=
                                "I get an error when I try to send an image!\n\n"
                                "Hints in SCP:SL have a size limit, so lowering pixel/color values is needed "
                                "when you encounter an error."
                                ,
                                width=300,
                                height=130,
                                disabled=True,
                                text_size=12,
                                multiline=True,
                                color="#ffffff",
                            )

                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ],
                    alignment=ft.MainAxisAlignment.CENTER
                )]
            ),
            width=678,
            height=618,
            scale=1,
            image_src=r"img/mountain-lake-minimalist-wallpaper-3440x1440_15.jpg",
            image_fit=ft.ImageFit.COVER,
            border_radius=15
        ))

        page.add(ui)
        page.update()
        page.visible = True


if __name__ == "__main__":
    formatter = Formatter()
    ft.app(target=formatter.main)
