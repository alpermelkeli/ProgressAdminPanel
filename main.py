import sys

import customtkinter as ctk

from tkinter import filedialog, messagebox

import threading

import time

from utils.Export import export_project

from utils.Upload import upload_animation_project, upload_render_project

import requests

from component.ScrollableLabelButtonFrameAnimation import ScrollableLabelButtonFrameAnimation

from component.ScrollableLabelButtonFrameRender import ScrollableLabelButtonFrameRender

from model.Project import Project

from constants.Constants import ADD_PROJECT_URL, REMOVE_PROJECT_URL, RESET_PROJECT_URL

from component.Icons import Icons


class ProjectTrackerApp:
    def __init__(self, root):

        self.dynamic_fields_frame = None

        self.root = root

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.title("DPI FARM STUDIO")

        self.root.iconbitmap("assets/logo.ico")

        self.projects = []

        self.reset_projects_button = ctk.CTkButton(self.root, text="Reset", fg_color="#333333", command=self.reset_projects, width=50)

        self.reset_projects_button.pack(pady=10)

        self.always_on_top_switch = ctk.CTkSwitch(self.root, text="Sürekli Üstte", command=self.toggle_always_on_top,
                                                  progress_color="grey", button_color="white",
                                                  onvalue="on", offvalue="off", fg_color="#333333")

        self.always_on_top_switch.pack(pady=10)

        logo_label = ctk.CTkLabel(self.root, image=Icons.get_icon(100, 130, "logo"), text="")

        logo_label.pack(pady=(10, 0))

        self.animation_frame = ScrollableLabelButtonFrameAnimation(root, edit_command=self.edit_selected_project,
                                                                   export_command=self.export_selected_project,
                                                                   remove_command=self.remove_project,
                                                                   upload_command=self.upload_selected_project,
                                                                   width=350, height=250)

        self.render_frame = ScrollableLabelButtonFrameRender(root, edit_command=self.edit_selected_project,
                                                             remove_command=self.remove_project,
                                                             upload_command=self.upload_selected_project,
                                                             width=350, height=250)

        self.animation_frame.pack(pady=10)
        self.render_frame.pack(pady=10)

        self.add_project_button = ctk.CTkButton(root, text="Yeni Proje Ekle", command=self.add_project,
                                                fg_color="#333333")
        self.add_project_button.pack(pady=10)

    def toggle_always_on_top(self):
        if self.always_on_top_switch.get() == "on":
            self.root.attributes("-topmost", True)
        else:
            self.root.attributes("-topmost", False)

    def on_closing(self):
        self.reset_projects()
        sys.exit()

    def reset_projects(self):
        for project in self.projects:
            project.tracking = False

        try:
            response = requests.post(RESET_PROJECT_URL)
            response.raise_for_status()

            if response.status_code == 200:
                for project in list(self.projects):
                    self.projects.remove(project)

                    if project.project_type == "Animation":
                        self.animation_frame.remove_item(project.id)
                    else:
                        self.render_frame.remove_item(project.id)

                messagebox.showinfo("Reset işlemi!", "Proje resetleme başarılı!")

            else:
                error_message = response.json().get('error', 'Unknown error')
                messagebox.showerror("Hata", f"Proje resetlenirken hata oluştu: {error_message}")

                for project in self.projects:
                    project.tracking = True

        except requests.RequestException as e:
            messagebox.showerror("Hata", f"Sunucuya bağlanırken hata oluştu: {e}")

            for project in self.projects:
                project.tracking = True

    def add_project(self):
        new_project_window = ctk.CTkToplevel(self.root)
        new_project_window.title("Yeni Proje Ekle")

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        new_project_window.geometry(f"{root_width}x{root_height}+{root_x}+{root_y}")
        new_project_window.focus_set()
        new_project_window.grab_set()

        ctk.CTkLabel(new_project_window, text="Proje Türü:").pack()
        project_type_var = ctk.StringVar(value="Animation")
        ctk.CTkRadioButton(
            new_project_window, height=50, text="Animation", variable=project_type_var, value="Animation",
            fg_color="#333333",
            command=lambda: self.update_project_fields(new_project_window, project_type_var.get())
        ).pack()
        ctk.CTkRadioButton(
            new_project_window, height=50, text="Render", variable=project_type_var, value="Render", fg_color="#333333",
            command=lambda: self.update_project_fields(new_project_window, project_type_var.get())
        ).pack()

        self.dynamic_fields_frame = ctk.CTkFrame(new_project_window, height=250)

        self.dynamic_fields_frame.configure(fg_color="transparent")

        self.dynamic_fields_frame.pack(fill="both", expand=False)

        self.update_project_fields(new_project_window, project_type_var.get())

        ctk.CTkLabel(new_project_window, text="Proje İsmi:").pack()
        project_name_entry = ctk.CTkEntry(new_project_window)
        project_name_entry.pack()

        ctk.CTkLabel(new_project_window, text="Klasör Konumu:").pack()
        folder_path_entry = ctk.CTkEntry(new_project_window)
        folder_path_entry.pack()
        folder_browse_button = ctk.CTkButton(new_project_window, fg_color="#333333", text="Gözat",
                                             command=lambda: self.browse_folder(folder_path_entry))
        folder_browse_button.pack()

        ctk.CTkLabel(new_project_window, text="Toplam Dosya Sayısı:").pack()
        total_files_entry = ctk.CTkEntry(new_project_window)
        total_files_entry.pack()

        ctk.CTkLabel(new_project_window, text="Bilgilendirme Mesajı:").pack()
        notification_message_entry = ctk.CTkEntry(new_project_window)
        notification_message_entry.insert(0, "Farmlanıyor...")
        notification_message_entry.pack()

        ctk.CTkLabel(new_project_window, text="Ödeme Linki:").pack()
        payment_link_entry = ctk.CTkEntry(new_project_window)
        payment_link_entry.pack()

        ctk.CTkLabel(new_project_window, text="GPU Sayısı:").pack()
        gpu_count_entry = ctk.CTkEntry(new_project_window)
        gpu_count_entry.pack()

        ctk.CTkLabel(new_project_window, text="Fiyat:").pack()

        price_frame = ctk.CTkFrame(new_project_window)
        price_frame.pack()

        price_entry = ctk.CTkEntry(price_frame, width=100)
        price_entry.grid(row=0, column=0, padx=5)

        currency_var = ctk.StringVar(value="₺")
        currency_options = ["$", "₺"]
        currency_menu = ctk.CTkOptionMenu(price_frame, variable=currency_var, values=currency_options, width=10,
                                          fg_color="#333333", button_color="#333333")
        currency_menu.grid(row=0, column=1, padx=5)

        add_button = ctk.CTkButton(
            new_project_window, text="Ekle", fg_color="#333333",
            command=lambda: self.save_project(
                new_project_window, project_name_entry, folder_path_entry, total_files_entry,
                notification_message_entry, payment_link_entry, gpu_count_entry, price_entry,
                project_type_var.get(), self.resolution_entry, self.frame_count_entry, currency_var
            )
        )
        add_button.pack(pady=10)

    def update_project_fields(self, window, project_type):
        for widget in self.dynamic_fields_frame.winfo_children():
            widget.destroy()

        if project_type == "Animation":

            ctk.CTkLabel(self.dynamic_fields_frame, text="Çözünürlük:").pack()
            self.resolution_entry = ctk.CTkOptionMenu(self.dynamic_fields_frame, fg_color="#333333",
                                                      button_color="#333333",
                                                      values=["640x360", "1280x720", "1920x1080", "2560x1440",
                                                              "3840x2160"])
            self.resolution_entry.pack()

            ctk.CTkLabel(self.dynamic_fields_frame, text="fps:").pack()
            self.frame_count_entry = ctk.CTkOptionMenu(self.dynamic_fields_frame, fg_color="#333333",
                                                       button_color="#333333", values=["25", "30", "60", "200"])
            self.frame_count_entry.pack()
        elif project_type == "Render":

            ctk.CTkLabel(self.dynamic_fields_frame, text="Çözünürlük:").pack()
            self.resolution_entry = ctk.CTkOptionMenu(self.dynamic_fields_frame, fg_color="#333333",
                                                      button_color="#333333",
                                                      values=["1280x720", "1920x1080", "3840x2160",
                                                              "7680x4320"])
            self.resolution_entry.pack()

    @staticmethod
    def browse_folder(entry):
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry.delete(0, ctk.END)
            entry.insert(0, folder_path)

    def save_project(self, window, name_entry, folder_entry, total_files_entry, message_entry, link_entry,
                     gpu_count_entry, price_entry, project_type, resolution_entry, frame_count_entry, currency_var):
        name = name_entry.get()
        folder_path = folder_entry.get()
        total_files = int(total_files_entry.get())
        notification_message = message_entry.get()
        payment_link = link_entry.get()
        gpu_count = gpu_count_entry.get()
        price_num = price_entry.get()
        currency = currency_var.get()
        price = f"{price_num} {currency}"
        resolution = resolution_entry.get()
        fps = frame_count_entry.get()

        if name and folder_path and total_files and notification_message:
            new_project = Project(name, folder_path, total_files, notification_message, payment_link,
                                  gpu_count=gpu_count, price=price, project_type=project_type, resolution=resolution,
                                  fps=fps)
            self.projects.append(new_project)

            target_frame = self.animation_frame if project_type == "Animation" else self.render_frame
            target_frame.add_item(new_project.id, new_project.name)

            threading.Thread(target=self.track_project, args=(new_project, target_frame.update_file_progress)).start()

            window.destroy()
        else:
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")

    def edit_selected_project(self, project_id):
        selected_project = next((project for project in self.projects if project.id == project_id), None)
        if selected_project is None:
            messagebox.showwarning("Hata", "Seçilen proje bulunamadı.")
            return
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Projeyi Düzenle")

        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        edit_window.geometry(f"{root_width}x{root_height}+{root_x}+{root_y}")
        edit_window.focus_set()
        edit_window.grab_set()

        ctk.CTkLabel(edit_window, text="Klasör Konumu:").pack()
        folder_path_entry = ctk.CTkEntry(edit_window)
        folder_path_entry.insert(0, selected_project.folder_path)
        folder_path_entry.pack()
        folder_browse_button = ctk.CTkButton(edit_window, text="Gözat", fg_color="#333333",
                                             command=lambda: self.browse_folder(folder_path_entry))
        folder_browse_button.pack()

        ctk.CTkLabel(edit_window, text="Toplam Dosya Sayısı:").pack()
        total_files_entry = ctk.CTkEntry(edit_window)
        total_files_entry.insert(0, str(selected_project.total_files))
        total_files_entry.pack()

        ctk.CTkLabel(edit_window, text="Bilgilendirme Mesajı:").pack()
        notification_message_entry = ctk.CTkEntry(edit_window)
        notification_message_entry.insert(0, selected_project.notification_message)
        notification_message_entry.pack()

        ctk.CTkLabel(edit_window, text="Bilgi Mesajı:").pack()
        information_message_entry = ctk.CTkTextbox(edit_window, height=150, width=300, corner_radius=20, border_width=1,
                                                   border_color="white")
        information_message_entry.insert("1.0",
                                         selected_project.information_message)  # Metni ilk satırın ilk sütununa ekler
        information_message_entry.pack()

        ctk.CTkLabel(edit_window, text="Ödeme Linki:").pack()
        payment_link_entry = ctk.CTkEntry(edit_window)
        payment_link_entry.insert(0, selected_project.payment_link)
        payment_link_entry.pack()

        ctk.CTkLabel(edit_window, text="Fiyat:").pack()

        price_frame = ctk.CTkFrame(edit_window)
        price_frame.pack()

        price_entry = ctk.CTkEntry(price_frame, width=100)

        price_entry.insert(0, selected_project.price.split(" ")[0])

        price_entry.grid(row=0, column=0, padx=5)

        currency_var = ctk.StringVar(value=selected_project.price.split(" ")[1])

        currency_options = ["$", "₺"]

        currency_menu = ctk.CTkOptionMenu(price_frame, variable=currency_var, values=currency_options, width=10,
                                          fg_color="#333333", button_color="#333333")

        currency_menu.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(edit_window, text="GPU Sayısı:").pack()
        gpu_count_entry = ctk.CTkEntry(edit_window)
        gpu_count_entry.insert(0, selected_project.gpu_count)
        gpu_count_entry.pack()

        save_button = ctk.CTkButton(edit_window, text="Kaydet", fg_color="#333333",
                                    command=lambda: self.update_project(edit_window, selected_project,
                                                                        folder_path_entry,
                                                                        total_files_entry, notification_message_entry,
                                                                        information_message_entry,
                                                                        payment_link_entry, gpu_count_entry,
                                                                        price_entry, currency_var))
        save_button.pack(pady=10)

    def upload_selected_project(self, project_id):
        selected_project = next((project for project in self.projects if project.id == project_id), None)
        if selected_project is None:
            messagebox.showwarning("Hata", "Seçilen proje bulunamadı.")
            return
        selected_project.exported = True
        selected_project.notification_message = "Upload ediliyor..."
        if selected_project.project_type == "Animation":
            threading.Thread(target=self.perform_animation_upload, args=(selected_project,)).start()
        else:
            threading.Thread(target=self.perform_render_upload, args=(selected_project,)).start()

    def perform_animation_upload(self, selected_project):

        upload_animation_project(selected_project,
                                 animation_upload_progress_callback=self.animation_upload_progress_callback)

    def perform_render_upload(self, selected_project):
        upload_render_project(selected_project, render_upload_progress_callback=self.render_upload_progress_callback)

    def export_selected_project(self, project_id):
        selected_project = next((project for project in self.projects if project.id == project_id), None)
        if selected_project is None:
            messagebox.showwarning("Hata", "Seçilen proje bulunamadı.")
            return

        selected_project.notification_message = "Birleştiriliyor..."

        threading.Thread(target=self.perform_export, args=(selected_project,)).start()

    def perform_export(self, selected_project):
        export_project(selected_project, self.update_export_status)

    def update_export_status(self, project_id):
        self.root.after(0, self._update_export_status, project_id)

    def _update_export_status(self, project_id):
        project = next((p for p in self.projects if p.id == project_id), None)
        if project:
            self.animation_frame.update_export_status(project_id, True)

    def animation_upload_progress_callback(self, project_id, upload_progress):
        project = next((p for p in self.projects if p.id == project_id), None)
        if project:
            project.upload_progress = upload_progress
            self.animation_frame.update_upload_progress(project_id, upload_progress)

    def render_upload_progress_callback(self, project_id, upload_progress):
        project = next((p for p in self.projects if p.id == project_id), None)
        if project:
            if project.upload_progress == 100:
                project.notification_message = "Ödeme bekleniyor..."

            project.upload_progress = upload_progress

            self.render_frame.update_upload_progress(project_id, upload_progress)

    def update_project(self, window, project, folder_entry, total_files_entry, message_entry, information_message_entry,
                       link_entry,
                       gpu_count_entry,
                       price_entry,
                       currency_var):
        folder_path = folder_entry.get()
        total_files = int(total_files_entry.get())
        notification_message = message_entry.get()
        information_message = information_message_entry.get("1.0", "end-1c")
        payment_link = link_entry.get()
        gpu_count = gpu_count_entry.get()
        price_num = price_entry.get()
        currency = currency_var.get()
        price = f"{price_num} {currency}"

        if folder_path and total_files and notification_message:
            project.folder_path = folder_path
            project.total_files = total_files
            project.notification_message = notification_message
            project.payment_link = payment_link
            project.gpu_count = gpu_count
            project.price = price
            project.information_message = information_message

            window.destroy()
        else:
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.")

    def remove_project(self, project_id):
        selected_project = next((project for project in self.projects if project.id == project_id), None)
        if selected_project is None:
            messagebox.showwarning("Hata", "Seçilen proje bulunamadı.")
            return
        data = {"project_id": selected_project.id}
        selected_project.tracking = False

        try:
            response = requests.post(REMOVE_PROJECT_URL, json=data)

            response.raise_for_status()
            if response.status_code == 200:

                messagebox.showinfo("Bilgi", "Proje başarıyla silindi.")
                self.projects.remove(selected_project)
                if selected_project.project_type == "Animation":
                    self.animation_frame.remove_item(project_id)
                else:
                    self.render_frame.remove_item(project_id)

            else:
                error_message = response.json().get('error', 'Unknown error')
                selected_project.tracking = True
                messagebox.showerror("Hata", f"Projeyi silerken hata oluştu: {error_message}")

        except requests.RequestException as e:
            selected_project.tracking = True
            messagebox.showerror("Hata", f"Sunucuya bağlanırken hata oluştu: {e}")

    @staticmethod
    def track_project(project, update_file_progress_callback):
        while project.tracking:
            try:
                project.getFileProgress()

                if project.exported:

                    if project.upload_progress == 100:
                        project.notification_message = "Ödeme Bekleniyor..."

                    data = {
                        "project_id": project.id,
                        "project_type": project.project_type,
                        "project_name": project.name,
                        "progress": project.upload_progress,
                        "message": project.notification_message,
                        "information_message": project.information_message,
                        "price": project.price,
                        "payment_link": project.payment_link,
                        "gpu_count": project.gpu_count,
                        "framerate": project.fps,
                        "resolution": project.resolution
                    }
                else:

                    data = {
                        "project_id": project.id,
                        "project_type": project.project_type,
                        "project_name": project.name,
                        "progress": project.file_progress,
                        "message": project.notification_message,
                        "information_message": project.information_message,
                        "price": project.price,
                        "payment_link": project.payment_link,
                        "gpu_count": project.gpu_count,
                        "framerate": project.fps,
                        "resolution": project.resolution
                    }

                requests.post(ADD_PROJECT_URL, json=data)

                update_file_progress_callback(project.id, project.file_progress)

            except Exception as e:
                messagebox.showerror("Hata", f"Hata: {e}")

            time.sleep(5)


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.geometry("400x920")
    app = ProjectTrackerApp(root)
    root.mainloop()
