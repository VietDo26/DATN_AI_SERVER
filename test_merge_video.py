import subprocess

def merge_images_video(video_path, start_image_path, end_image_path, output_path, duration=3, fps=30):
  """
  Merges images at the beginning and end of a video using ffmpeg.

  Args:
      video_path (str): Path to the input video file.
      start_image_path (str): Path to the image to be inserted at the beginning.
      end_image_path (str): Path to the image to be inserted at the end.
      output_path (str): Path to the output video file.
      duration (int, optional): Duration (in seconds) to display each image. Defaults to 5.
      fps (int, optional): Frame rate of the output video. Defaults to 24.
  """

  # Silence generation (optional for consistency if video has audio)
  silence_duration = str(int(duration * fps))  # Calculate duration in frames
  silence_cmd = f"ffmpeg -f lavfi -t {silence_duration} -i anullsrc=channel_layout=stereo:sample_rate=44100 silence.wav"

  # Image to video conversion (optional for consistency with fps)
  start_image_cmd = f"ffmpeg -loop 1 -framerate {fps} -t {duration} -i {start_image_path} start_image.mp4"
  end_image_cmd = f"ffmpeg -loop 1 -framerate {fps} -t {duration} -i {end_image_path} end_image.mp4"

  # Concatenate with video using filter_complex
  filter_complex = "[0:v]scale=in_w:-1[start_v]; [1:v] [start_v] concat=n=2:v=1:a=0 [concat_v]; "
  filter_complex += "[concat_v] [2:v] concat=n=2:v=1:a=0 [final_v]; [0:a] [silence.wav] concat=n=2:a=1 [final_a]"

  # Main command to merge with appropriate video and audio handling
  if "-c:v libx264" in video_path:  # Check for H.264 encoding
    output_cmd = f"ffmpeg -i {video_path} -loop 1 -i start_image.mp4 -loop 1 -i end_image.mp4 -filter_complex '{filter_complex}' -map '[final_v]' -map '[final_a]' -c:v copy -c:a copy {output_path}"
  else:  # Use copy for other codecs (adjust as needed)
    output_cmd = f"ffmpeg -i {video_path} -loop 1 -i start_image.mp4 -loop 1 -i end_image.mp4 -filter_complex '{filter_complex}' -map '[final_v]' -map '[final_a]' {output_path}"

  # Generate silence (optional)
  subprocess.run(silence_cmd.split(), check=True)

  # Convert images to video (optional)
  subprocess.run(start_image_cmd.split(), check=True)
  subprocess.run(end_image_cmd.split(), check=True)

  # Perform the merging
  subprocess.run(output_cmd.split(), check=True)

  # Clean up temporary files (optional)
  subprocess.run(["rm", "silence.wav", "start_image.mp4", "end_image.mp4"], check=True)

# Example usage
video_path = "video_5s.mp4"
start_image_path = "Warning.jpg"
end_image_path = "Warning.png"
output_path = "merged_video.mp4"

merge_images_video(video_path, start_image_path, end_image_path, output_path)

print("Video merging complete!")
