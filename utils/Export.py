import subprocess
import os


def export_project(selected_project, export_project_callback):

    filepath = selected_project.folder_path

    fps = selected_project.fps

    resolution = selected_project.resolution

    if not os.path.exists(filepath):
        print(f"Error: Path {filepath} does not exist.")
        return

    output_video = os.path.join(filepath, f"{selected_project.id}.mp4")

    command = [
        "ffmpeg",
        "-framerate", fps,
        "-i", os.path.join(filepath, f"1_%05d.tga"),
        "-s", resolution,
        "-c:v", "libx264",
        "-b:v", "65M",
        "-pix_fmt", "yuv420p",
        output_video
    ]

    try:
        subprocess.run(command, check=True)

        selected_project.exported = True

        export_project_callback(selected_project.id)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while exporting video: {e}")