from PIL import Image
from customtkinter import CTkImage


class Icons:

    @staticmethod
    def get_icon(width: int,height:int, icon_name: str):
        icon = Image.open(f"assets/{icon_name}.png")

        resized_icon = icon.resize((width, height), Image.Resampling.LANCZOS)

        icon_image = CTkImage(resized_icon, size=(width, height))

        return icon_image

