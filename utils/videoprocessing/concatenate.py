from moviepy.editor import *
from pathlib import Path
import sys
import os

# sys.path.append(str(Path(__file__).parent))
folder_path= str(Path(__file__).parent)

def concatenateWarning(video_path: str, output_path:str):
    path_clip_warning = os.path.join(folder_path,'warning_fullhd.mp4')
    clip = VideoFileClip(video_path)
    clip_warning = VideoFileClip(path_clip_warning)
    # print(f'clip original : Width x Height = {clip.w}x{clip.h}')
    # print(f'clip warning : Width x Height = {clip_warning.w}x{clip_warning.h}')
    clip_warning_resize = clip_warning.resize( (clip.w,clip.h) )
    # print(clip_warning_resize.w,clip_warning_resize.h)
    final = concatenate_videoclips([clip_warning_resize, clip, clip_warning_resize])
    final.write_videofile(output_path)
