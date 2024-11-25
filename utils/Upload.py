from repository.GoogleCloudApi import GoogleCloudApi
import os
import shutil

api = GoogleCloudApi()


def upload_animation_project(selected_project, animation_upload_progress_callback):
    api.upload_file_to_gcs(selected_project.folder_path + f"/{selected_project.id}.mp4",
                           project_id=selected_project.id,
                           upload_progress_callback=animation_upload_progress_callback
                           )

    api.make_animation_blob_public(selected_project.id)


def zip_folder(input_folder, output_folder, zip_name):
    if os.path.abspath(input_folder) == os.path.abspath(output_folder):
        raise Exception("Zip dosyası kaydedilecek dizin, ziplenecek dizin ile aynı olamaz.")

    zip_path = os.path.join(output_folder, zip_name)
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', input_folder)
    return f"{zip_path}.zip"

def upload_render_project(selected_project, render_upload_progress_callback):
    parent_folder = os.path.dirname(selected_project.folder_path)

    output_folder = os.path.join(parent_folder, 'output')
    os.makedirs(output_folder, exist_ok=True)

    zip_file_path = zip_folder(selected_project.folder_path, output_folder, selected_project.id)

    api.upload_file_to_gcs(zip_file_path,
                           project_id=selected_project.id,
                           upload_progress_callback=render_upload_progress_callback)

    api.make_render_blob_public(selected_project.id)

    os.remove(zip_file_path)
