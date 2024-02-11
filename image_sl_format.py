from PIL import Image
import random
import time
import pyperclip
import flet as ft
import os
import requests


class Formatter:
    def __init__(self):
        self.file_path: str = ""
        self.transparency: bool = False
        self.img_size: int = 0
        self.output: str = ""
        self.color_amount: int = 0
        self.valid_file_path: bool = False
        self.output_name: str = ""
        self.folder: str = f"{os.path.expanduser('~')}\\scpsl_img"
        self.bytes: int = 0
        self.can_redirect: bool = True
        self.MAX_BYTE_SIZE: int = 65534
        self.formatting: bool = False
        self.format_for_se: bool = False
        self.format_for_cmd: bool = False

    def rgb_to_hex(self, rgb) -> str:
        if self.transparency:
            return "#{:02X}{:02X}{:02X}{:02X}".format(*rgb)

        return "#{0:02x}{1:02x}{2:02x}".format(rgb[0], rgb[1], rgb[2])

    def format_image(self, *, create_previev: bool) -> None:
        self.bytes = 0
        self.formatting = True
        print("Formatting an image..."
              f"\n> {self.file_path = }"
              f"\n> {self.img_size = }"
              f"\n> {self.color_amount = }"
              f"\n> {self.transparency = }"
              f"\n")

        image = Image.open(self.file_path)
        org_width, org_height = image.size
        size_multiplier: float = (
            int(self.img_size) / org_width
            if org_width >= org_height else
            int(self.img_size) / org_height
        )

        width, height = int(round(org_width * size_multiplier, 1)), int(round(org_height * size_multiplier, 1))
        if width == 0 or height == 0:
            self.formatting = False
            return

        image = image.resize((width, height))

        image = image.convert(
            "P",
            colors=self.color_amount,
            palette=Image.ADAPTIVE
        )

        image = image.convert('RGBA') if self.transparency else image.convert('RGB')

        last_hex: str = ""
        if self.format_for_cmd:
            self.output = "act HINT 10 "

        elif self.format_for_se:
            self.output = "HINT 10 "

        else:
            self.output = ""

        self.output += "<size=5><line-height=84%>"
        self.bytes += len(self.output)

        for y in range(height):
            for x in range(width):
                pixel = image.getpixel((x, y))
                hex_value = self.rgb_to_hex(pixel)

                if not last_hex == hex_value:
                    self.output += f"<color={hex_value}>█"

                    if self.transparency:
                        self.bytes += 20
                    else:
                        self.bytes += 18

                elif last_hex == hex_value:
                    self.bytes += 3
                    self.output += "█"

                last_hex = hex_value

            self.bytes += 2
            self.output += r"\n"

        print("Image has been formatted!"
              f"\n> {self.bytes = }"
              f"\n")

        if not create_previev or self.bytes > self.MAX_BYTE_SIZE:
            self.formatting = False
            return

        for filename in os.listdir(self.folder):
            if filename.endswith("_output.png"):
                try:
                    os.remove(os.path.join(self.folder, filename))
                except PermissionError:
                    print(f"!-- Could not remove file {filename}\n")

        self.output_name = f"{self.folder}/{str(random.randint(11111111111111111, 99999999999999999))}_output.png"
        diff_multiplier = 1920 / org_width

        image = image.resize(
            (int(org_width * diff_multiplier),
             int(org_height * diff_multiplier)),
            Image.NEAREST
        )
        image.save(self.output_name)

        print(f"Image has been saved as {self.output_name}\n")

        self.formatting = False
        return

    def main(self, page: ft.Page) -> None:
        page.visible = False
        page.title = "Image Formatter for SCP SL"
        page.window_resizable = False
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"
        page.window_width = 750
        page.window_height = 635
        page.window_maximizable = False
        page.theme_mode = "light"
        page.bgcolor = "#00000000"
        page.window_bgcolor = "#00000000"

        def change_for_se_formatting(_):
            self.format_for_se = True if self.format_for_se is not True else False
            if not self.format_for_se:
                se_command_format_checkbox.disabled = True
                se_command_format_checkbox.value = False
                self.format_for_cmd = False
            else:
                se_command_format_checkbox.disabled = False

            se_command_format_checkbox.update()
            print(f"{self.format_for_se = }")

        def change_for_cmd_formatting(_):
            self.format_for_cmd = True if self.format_for_cmd is not True else False
            print(f"{self.format_for_cmd = }")

        def show_formatted_img(e) -> None:
            """
            Shows the formatted image previev and executes update_visible_values function
            :param e:
            :return: None
            """
            output_img.visible = True
            output_img.src = self.output_name
            arrow_right.visible = True
            page.update()
            update_visible_values()
            show_formatted_popup(e)

        def update_visible_values() -> None:
            """
            Updates all visible parameter values to the "self" ones
            :return: None
            """
            image_colors.value = self.color_amount
            image_size.value = self.img_size
            image_transparency.value = "✔ Yes" if self.transparency else "❌ No"
            page.update()

        def get_provided_values() -> None:
            """
            Updates all "self" parameter values to the ones provided by the user
            :return: None
            """
            self.img_size = int(image_size.value)
            self.color_amount = int(image_colors.value)
            self.transparency = True if image_transparency.value == "✔ Yes" else False

        def provided_values_correct(check_img_size: bool = True, check_img_colors: bool = True) -> bool:
            """
            Checks if all values provided by the user are correct
            Will light up text field if value is incorrect
            :param check_img_size: Checks provided size
            :param check_img_colors: Checks provided color amount
            :return: bool
            """
            def change_to_red(text_field: ft.TextField):
                text_field.border_color = ft.colors.RED
                text_field.update()

            def reset_color(text_field: ft.TextField):
                text_field.border_color = ft.colors.BLACK
                text_field.update()

            if not self.valid_file_path:
                page.update()
                return False

            if check_img_size:
                try:
                    int(image_size.value)
                except ValueError:
                    change_to_red(image_size)
                    return False

                if int(image_size.value) > 300 or int(image_size.value) < 2:
                    change_to_red(image_size)
                    return False

            reset_color(image_size)

            if check_img_colors:
                try:
                    int(image_colors.value)
                except ValueError:
                    change_to_red(image_colors)
                    return False

                if int(image_colors.value) > 256 or int(image_colors.value) < 1:
                    change_to_red(image_colors)
                    return False

            reset_color(image_colors)

            return True

        def is_under_hint_limit(*, create_previev: bool, change_color_if_incorrect: bool) -> bool:
            """
            Check if the image size is within the SCP:SL hint size limit
            :return: bool
            """
            self.format_image(create_previev=create_previev)

            if change_color_if_incorrect and self.bytes > self.MAX_BYTE_SIZE:
                image_colors.border_color = ft.colors.RED
                image_size.border_color = ft.colors.RED
                image_colors.update()
                image_size.update()

            return True if self.bytes <= self.MAX_BYTE_SIZE else False

        def one_to_one_format(e) -> None:
            """
            Formats the image with the "1:1" mode
            :param e:
            :return: None
            """
            if self.formatting:
                return

            if not provided_values_correct(check_img_size=False, check_img_colors=False):
                return

            image = Image.open(image_file_path.value)

            width, height = image.size
            self.img_size = width if width >= height else height

            self.transparency = True if image.mode == 'RGBA' else False

            image = image.convert('P', palette=Image.ADAPTIVE, colors=256)
            self.color_amount = len(image.getcolors())

            update_visible_values()

            page.update()

            if provided_values_correct():
                self.format_image(create_previev=True)
                show_formatted_img(e)

        def standard_format(e):
            """
            Formats the image with the "standard" mode
            :param e:
            :return: None
            """

            if self.formatting:
                return

            if not provided_values_correct():
                return

            get_provided_values()

            if not is_under_hint_limit(create_previev=True, change_color_if_incorrect=True):
                return

            show_formatted_img(e)

        def smart_format_button_clicked(_):
            def max_pixels(e):
                if self.formatting:
                    close(e)
                    return

                if not provided_values_correct(check_img_size=False):
                    close(e)
                    return

                get_provided_values()

                self.img_size = 2

                while is_under_hint_limit(create_previev=False, change_color_if_incorrect=False):
                    self.img_size += 2

                self.img_size -= 2
                self.format_image(create_previev=True)

                close(e)
                update_visible_values()
                show_formatted_img(e)
                smart_format_alert.open = False
                smart_format_alert.update()
                return

            def max_colors(e):
                if self.formatting:
                    close(e)
                    return

                if not provided_values_correct(check_img_colors=False):
                    close(e)
                    return

                get_provided_values()

                self.color_amount = 1

                if not is_under_hint_limit(create_previev=False, change_color_if_incorrect=True):
                    close(e)
                    return

                image = Image.open(self.file_path)
                width, height = image.size

                size_multiplier = int(self.img_size) / width if width >= height else int(self.img_size) / height

                width, height = int(round(width * size_multiplier, 1)), int(round(height * size_multiplier, 1))
                image = image.resize((width, height))

                image = image.convert('P', palette=Image.ADAPTIVE, colors=256)
                max_colors = len(image.getcolors())

                color_addition_step = 5

                while (self.bytes < self.MAX_BYTE_SIZE and
                       abs(self.color_amount - max_colors) > color_addition_step / 2):

                    self.color_amount += color_addition_step
                    self.format_image(create_previev=False)

                close(e)
                self.color_amount -= color_addition_step
                self.format_image(create_previev=True)
                update_visible_values()
                smart_format_alert.open = False
                smart_format_alert.update()
                show_formatted_img(e)
                return

            def close(_):
                if self.formatting:
                    return
                smart_format_alert.open = False
                page.update()

            smart_format_alert = ft.AlertDialog(
                title=ft.Text(f"Which setting do you want to max out?"),
                modal=True,
                actions=[
                    ft.TextButton("Pixels", on_click=max_pixels, icon=ft.icons.ASPECT_RATIO_ROUNDED),
                    ft.TextButton("Colors", on_click=max_colors, icon=ft.icons.COLOR_LENS_OUTLINED),
                    ft.TextButton("Dismiss", on_click=close, icon=ft.icons.CANCEL_OUTLINED)
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_AROUND
            )

            page.dialog = smart_format_alert
            smart_format_alert.open = True
            page.update()
            return

        def changed_file_path(_):
            image_file_path.value = str(image_file_path.value).replace("\"", "")

            selected_img.src = "vanish"
            arrow_right.visible = False
            output_img.visible = False
            image_file_path.border_color = ft.colors.RED

            if os.path.isfile(image_file_path.value):
                self.valid_file_path = True
                selected_img.src = image_file_path.value
                self.file_path = image_file_path.value
                image_file_path.border_color = ft.colors.BLACK

            page.update()

        def copy_to_clipboard(_):
            copy_button.icon = ft.icons.CHECK_CIRCLE_OUTLINED
            copy_button.update()
            time.sleep(0.15)

            pyperclip.copy(self.output)
            image_formatted_popup.open = False
            image_formatted_popup.update()

            time.sleep(1)
            copy_button.icon = ft.icons.COPY_ROUNDED
            copy_button.update()

        def show_formatted_popup(_):
            image_formatted_popup.open = True
            image_formatted_popup.update()

        def show_settings(_):
            settings_popup.open = True
            settings_popup.update()

        def download_img(_):
            url = (r"https://github.com/Elektryk-Andrzej/"
                   r"Image-Formatter-for-SCP-SL/assets/100864896/5ddb16e6-9ffe-4744-8068-551057ad267d")

            data = requests.get(url).content
            with open(f'{self.folder}\\bg.jpg', 'wb') as file:
                file.write(data)

            downloaded_alert = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    f"\"bg.jpg\" has been downloaded.\n"
                    f"Restart the program for changes to take place.",
                    text_align=ft.TextAlign.CENTER
                ),
                actions_alignment=ft.MainAxisAlignment.CENTER
            )
            page.add(downloaded_alert)
            page.dialog = downloaded_alert
            downloaded_alert.open = True
            page.update()

        settings_button = ft.IconButton(
            icon=ft.icons.MENU,
            on_click=show_settings
        )

        def pick_files_result(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            image_file_path.value = e.files[0].path
            image_file_path.update()
            changed_file_path(None)

        filepicker_button = ft.IconButton(
            icon=ft.icons.IMAGE_SEARCH,
            on_click=lambda _: pick_files_dialog.pick_files()
        )

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        page.overlay.append(pick_files_dialog)

        se_script_format_checkbox = ft.Checkbox(
            label="Format hints to an SE script?",
            value=False,
            on_change=change_for_se_formatting,
            scale=ft.Scale(1.4, alignment=ft.Alignment(-1, 0))
        )

        se_command_format_checkbox = ft.Checkbox(
            label="Format hints to an SE command?",
            value=False,
            on_change=change_for_cmd_formatting,
            scale=ft.Scale(1.4, alignment=ft.Alignment(-1, 0)),
            disabled=True
        )

        settings_popup = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Text(
                        value="ScriptedEvents integration settings",
                        scale=ft.Scale(2, alignment=ft.Alignment(0, 3))
                    ),
                    se_script_format_checkbox,
                    se_command_format_checkbox
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30

                ),
                padding=30,
                width=600,
                border_radius=ft.border_radius.vertical(10, 0),
                #alignment=ft.Alignment(0, 0)
            )
        )

        settings_popup.open = False
        page.overlay.append(settings_popup)

        copy_button = ft.FilledButton(
            "Copy to clipboard",
            on_click=copy_to_clipboard,
            width=200, height=50,
            icon=ft.icons.COPY,
        )

        image_formatted_popup = ft.BottomSheet(
            ft.Container(
                ft.Row(
                    [copy_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=30,
                width=260,
                border_radius=ft.border_radius.vertical(10, 0),
            ),
            open=True
        )
        image_formatted_popup.open = False
        page.overlay.append(image_formatted_popup)

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
            src=self.output_name,
            error_content=no_img_selected,
            visible=False,
            tooltip="In-game image will look like this",
        )

        image_file_path = ft.TextField(
            label="Image path",
            prefix_icon=ft.icons.TERMINAL_ROUNDED,
            on_change=changed_file_path,
            border_color=ft.colors.RED,
            width=445,
            hint_text="e.g. boykisser.jpg",
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700
            )
        )
        second_level_width: int = 180

        image_transparency = ft.Dropdown(
            label="Transparency",
            value="❌ No",
            options=[
                ft.dropdown.Option("✔ Yes"),
                ft.dropdown.Option("❌ No"),
            ],
            prefix_icon=ft.icons.REMOVE_RED_EYE_OUTLINED,
            width=second_level_width,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700,
                color=ft.colors.BLACK
            )
        )

        image_size = ft.TextField(
            label="Pixel count",
            value="21",
            prefix_icon=ft.icons.ASPECT_RATIO_ROUNDED,
            width=second_level_width,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700
            )
        )

        image_colors = ft.TextField(
            label="Color count",
            width=second_level_width,
            value="37",
            prefix_icon=ft.icons.COLOR_LENS_OUTLINED,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.W_700
            )

        )

        button_style = ft.ButtonStyle(
            color={
                ft.MaterialState.DEFAULT: "#ddffffff",
                ft.MaterialState.HOVERED: "#ff000000"
            },
            bgcolor={
                ft.MaterialState.DEFAULT: "#01ffffff",
                ft.MaterialState.HOVERED: "#48ffffff"
            },
            elevation={
                ft.MaterialState.PRESSED: 0,
                ft.MaterialState.DEFAULT: 10
            },
            shadow_color=ft.colors.BLACK,
            overlay_color="#11ffffff",
            animation_duration=5,
            surface_tint_color="#55fca68b"

        )

        format_button = ft.ElevatedButton(
            text="Format",
            icon=ft.icons.ROTATE_LEFT,
            on_click=standard_format,
            style=button_style
        )

        smart_format_button = ft.ElevatedButton(
            text="Smart format",
            icon=ft.icons.AUTO_AWESOME_OUTLINED,
            on_click=smart_format_button_clicked,
            style=button_style
        )

        one_to_one_format_button = ft.ElevatedButton(
            text="1:1 format",
            icon=ft.icons.IMAGE_ASPECT_RATIO_ROUNDED,
            on_click=one_to_one_format,
            style=button_style
        )

        arrow_right = ft.Icon(
            name=ft.icons.DOUBLE_ARROW_ROUNDED,
            size=50,
            color="#cc000000",
            visible=False
        )

        ui = (ft.Container(
            ft.Stack([
                ft.Column([
                    ft.Column([
                        ft.Row(
                            [filepicker_button, image_file_path, settings_button],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),

                        ft.Row(
                            [image_transparency, image_size, image_colors],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ]),

                    ft.Row(
                        [selected_img, arrow_right, output_img],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),

                    ft.Row(
                        [one_to_one_format_button, format_button, smart_format_button],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        spacing=45
                    ),
                ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )]
            ),
            width=700,
            height=560,
            image_src=f"{self.folder}\\bg.jpg",
            image_fit=ft.ImageFit.COVER,
            border_radius=10,

        ))

        page.add(ui)
        page.update()
        time.sleep(0.5)

        if os.path.isfile(f"{self.folder}/bg.jpg"):
            return

        no_bg_alert = ft.AlertDialog(
            title=ft.Text(
                f"No \"bg.jpg\" file found in {self.folder}\n"
                f"Downloading...",
                text_align=ft.TextAlign.CENTER
            ),
            actions_alignment=ft.MainAxisAlignment.CENTER,
            on_dismiss=download_img
        )
        page.opacity = 1
        page.bgcolor = "#928fcc"
        page.dialog = no_bg_alert
        no_bg_alert.open = True
        page.update()


if __name__ == "__main__":
    if not os.path.isdir(f"{os.path.expanduser('~')}/scpsl_img"):
        os.mkdir(f"{os.path.expanduser('~')}/scpsl_img")

    formatter = Formatter()
    ft.app(target=formatter.main)
