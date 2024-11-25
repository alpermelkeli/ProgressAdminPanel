import customtkinter as ctk
import pyperclip

from component.AnimationItem import AnimationItem
from constants.Constants import WEBSITE_LINK, UPLOAD_LINK
from tkinter import messagebox

class ScrollableLabelButtonFrameAnimation(ctk.CTkScrollableFrame):
    def __init__(self, master, edit_command=None, export_command=None, remove_command=None, upload_command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.configure(fg_color="transparent", border_width=2, corner_radius=20)

        self.edit_command = edit_command
        self.export_command = export_command
        self.remove_command = remove_command
        self.upload_command = upload_command

        self.items = []

        self.header_label = ctk.CTkLabel(
            self,
            text="Animation",
            font=("Arial", 16, "bold"),
            padx=5,
            pady=10,
        )

        self.header_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")

    def copy_to_clipboard(self, text):
        messagebox.showinfo("Bilgi", "Link kopyalandı.")
        pyperclip.copy(text)

    def add_item(self, item_id, item_name, progress=0, exported=False, image=None):
        item = AnimationItem(self, item_id, item_name, progress, exported, image)

        if self.edit_command is not None:
            item.edit_button.configure(command=lambda: self.edit_command(item_id))

        if self.export_command is not None:
            item.export_button.configure(command=lambda: self.export_command(item_id))

        if self.remove_command is not None:
            item.remove_button.configure(command=lambda: self.remove_command(item_id))

        if self.upload_command is not None:
            item.upload_button.configure(command=lambda: self.upload_command(item_id))

        item.link_button.configure(command=lambda: self.copy_to_clipboard(f"{WEBSITE_LINK}{item_id}"))
        item.upload_link_button.configure(command=lambda: self.copy_to_clipboard(f"{UPLOAD_LINK}{item_id}.mp4"))

        self.items.append(item)
        item.row_index = len(self.items)

        item.frame.grid(row=item.row_index, column=0, columnspan = 3,pady=(0, 10), sticky="ew")

    def update_file_progress(self, id, file_progress):
        for item in self.items:
            if item.item_id == id:
                item.update_file_progress(file_progress)
                return

    def update_export_status(self, item_id, exported):
        for item in self.items:
            if item.item_id == item_id:
                item.update_export_status(exported)
                return

    def update_upload_progress(self, item_id, progress):
        for item in self.items:
            if item.item_id == item_id:
                item.update_upload_progress(progress)
                return

    def remove_item(self, item_id):
        for item in self.items:
            if item.item_id == item_id:
                item.destroy()
                self.items.remove(item)
                break
