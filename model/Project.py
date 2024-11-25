# In model/Project.py
import uuid
import os


class Project:
    def __init__(self, name, folder_path, total_files, notification_message, payment_link, gpu_count, price="0",
                 project_type="Animation", resolution="1920x1080", fps="30"):
        self.id = "{0}_dpifarmstudio_{1}".format(name, str(uuid.uuid4()))
        self.name = name
        self.folder_path = folder_path
        self.total_files = total_files
        self.notification_message = notification_message
        self.information_message = "Sizin için çalışıyoruz..."
        self.payment_link = payment_link
        self.gpu_count = gpu_count
        self.price = price
        self.project_type = project_type
        self.resolution = resolution
        self.fps = fps
        self.file_progress = 0
        self.upload_progress = 0
        self.tracking = True
        self.exported = False

    def getFileProgress(self):
        current_files = len(os.listdir(self.folder_path))
        self.file_progress = (current_files / self.total_files) * 100
