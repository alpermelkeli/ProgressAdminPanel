import customtkinter as ctk
from component.Icons import Icons
from component.CtkToolTip import CTkToolTip


class RenderItem:
    def __init__(self, frame, item_id, item_name, progress=0, image=None):
        self.frame = ctk.CTkFrame(frame, fg_color="#333333", border_width=1, border_color="black")

        self.frame.grid_anchor("center")
        for i in range(11):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_rowconfigure(i, weight=1)
        self.item_id = item_id
        self.item_name = item_name
        self.progress = progress
        self.image = image

        self.label = ctk.CTkLabel(self.frame, text=item_name, wraplength=100, fg_color="transparent", image=image,
                                  width=25, height=10, font=("Arial", 12, "bold"))
        self.file_progress_label = ctk.CTkLabel(self.frame, text=f"%{progress:.2f}", fg_color="transparent")
        self.edit_button = ctk.CTkButton(self.frame, text="", image=Icons.get_icon(15,15, icon_name="settings"),
                                         width=10, height=10, fg_color="transparent")
        self.link_button = ctk.CTkButton(self.frame, text="", image=Icons.get_icon(15,15, "link"), width=10, height=10,
                                         fg_color="transparent")
        self.remove_button = ctk.CTkButton(self.frame, text="", image=Icons.get_icon(15,15, "delete"), width=10, height=10,
                                           fg_color="transparent")

        self.upload_button = ctk.CTkButton(self.frame, text="", image=Icons.get_icon(15,15, "upload"), width=10, height=10,
                                           fg_color="transparent")
        self.upload_progress_label = ctk.CTkLabel(self.frame, text="0.00%", fg_color="transparent")
        self.upload_link_button = ctk.CTkButton(self.frame, text="", image=Icons.get_icon(15,15,  "link"), width=10,
                                                height=10, fg_color="transparent")

        self.label.grid(row=0, column=0, columnspan=5, pady=2, padx=2, sticky="ew")
        self.file_progress_label.grid(row=0, column=6, pady=2, sticky="ew")
        self.edit_button.grid(row=0, column=7, pady=2, padx=1, sticky="ew")
        self.link_button.grid(row=0, column=8, pady=2, padx=1, sticky="ew")
        self.remove_button.grid(row=0, column=9, pady=2, padx=1, sticky="ew")

        self.upload_button.grid(row=1, column=0, pady=2, padx=1, sticky="ew")
        self.upload_progress_label.grid(row=1, column=6, pady=2, padx=1, sticky="ew")
        self.upload_link_button.grid(row=1, column=9, pady=2, padx=1, sticky="ew")

        self.tooltip = CTkToolTip(self.label, self.item_name)

    def update_file_progress(self, progress):
        self.file_progress_label.configure(text=f"%{progress:.2f}")

    def update_upload_progress(self, progress):
        self.upload_progress_label.configure(text=f"%{progress:.2f}")

    def destroy(self):
        self.label.destroy()
        self.edit_button.destroy()
        self.file_progress_label.destroy()
        self.remove_button.destroy()
        self.link_button.destroy()
        self.upload_button.destroy()
        self.upload_progress_label.destroy()
        self.upload_link_button.destroy()
        self.frame.destroy()
