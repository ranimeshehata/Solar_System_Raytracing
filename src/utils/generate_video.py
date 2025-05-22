import imageio
import os

def generate_video_from_frames(input_dir, output_path, fps=1):
    images = sorted([img for img in os.listdir(input_dir) if img.endswith(".png")])
    if not images:
        raise ValueError("No frames found.")

    writer = imageio.get_writer(output_path, fps=fps, format='FFMPEG') 

    for filename in images:
        image_path = os.path.join(input_dir, filename)
        frame = imageio.imread(image_path)
        writer.append_data(frame)

    writer.close()
    print(f"Video saved to {output_path}")
