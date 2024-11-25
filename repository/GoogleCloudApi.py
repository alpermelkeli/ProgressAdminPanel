from google.cloud import storage
from google.oauth2 import service_account
import os
import requests

from constants.Constants import SERVICE_ACCOUNT_FILE, BUCKET_NAME


class GoogleCloudApi:


    @staticmethod
    def upload_file_to_gcs(file_path, project_id, upload_progress_callback):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE)
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(BUCKET_NAME)

        blob = bucket.blob(os.path.basename(file_path))

        def upload_file_with_progress(file_path, blob):
            upload_url = blob.create_resumable_upload_session()

            file_size = os.path.getsize(file_path)
            chunk_size = 5 * 1024 * 1024  # 5 MB
            current_pos = 0

            with open(file_path, 'rb') as file_obj:
                while current_pos < file_size:
                    chunk = file_obj.read(chunk_size)
                    headers = {
                        'Content-Range': f'bytes {current_pos}-{current_pos + len(chunk) - 1}/{file_size}'
                    }
                    response = requests.put(
                        upload_url,
                        headers=headers,
                        data=chunk
                    )

                    if response.status_code >= 400:
                        raise Exception(f'Upload failed: {response.text}')

                    current_pos += len(chunk)
                    upload_progress_callback(project_id, current_pos / file_size * 100)

            response = requests.post(upload_url)
            if response.status_code == 200:
                return blob.public_url
            else:
                raise Exception(f'Upload failed: {response.text}')

        return upload_file_with_progress(file_path, blob)

    @staticmethod
    def make_animation_blob_public(project_id):
        storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{project_id}.mp4")
        blob.make_public()

    @staticmethod
    def make_render_blob_public(project_id):
        storage_client = storage.Client.from_service_account_json(SERVICE_ACCOUNT_FILE)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{project_id}.zip")
        blob.make_public()