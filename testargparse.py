import platform
import subprocess
import signal
print(platform.system())

# def convert_video( source_paths:list,
#                    target_path: str,
#                    output_path: str,
#                    skip_download: bool = None,
#                    headless: bool = True,
#                    log_level: str = 'info',
#                    execution_providers: list =['cpu'],
#                    execution_thread_count:int = 4,
#                    execution_queue_count: int =1,
#                    video_memory_strategy: str ='strict',
#                    system_memory_limit: int =0,
#                    face_analyser_order: str = 'face_analyser_order',
#                    face_analyser_age: str = None,
#                    face_analyser_gender: str = 'male',
#                    face_detector_model: str ='yoloface',
#                    face_detector_size: str = '640x640',
#                    face_detector_score: float = 0.7,
#                    face_landmarker_score: float = 0.5,
#                    face_selector_mode: str = 'reference',
#                    reference_face_position: int =0,
#                    reference_face_distance: float = 0.8,
#                    reference_frame_number: int=100,
#                    face_mask_types : str = 'box',
#                    face_mask_blur: float = 0.6,
#                    face_mask_padding: list = [0, 0, 0, 0],
#                    face_mask_regions: list =['skin', 'left-eyebrow', 'right-eyebrow', 'left-eye', 'right-eye', 'eye-glasses', 'nose', 'mouth', 'upper-lip', 'lower-lip'],
#                    trim_frame_start: int = None,
#                    trim_frame_end: int = None,
#                    temp_frame_format: str = 'png',
#                    keep_temp: bool = True,
#                    output_image_quality: int = 100,
#                    args_output_image_resolution: str = None,
#                    output_video_encoder: str = 'libx264',
#                    output_video_preset: str = 'ultrafast',
#                    output_video_quality: int = 100,
#                    args_output_video_resolution : str= None,
#                    args_output_video_fps : float = None,
#                    skip_audio: bool = None,
#                    frame_processors : list = ['face_swapper'],
#                    ui_layouts : list = ['default']
#                    ):
#     source = 'source_paths='+source_paths
#     print

# convert_video(source_paths='./imageRonaldo.jpg')
# a = "python3 run.py --headless --source='./imageRonaldo.jpg' --target='./video_5s.mp4' --output='./mp4swapped.mp4' --execution-providers='cuda' --frame-processors='face_swapper' --face-swapper-model='inswapper_128_fp16'"
subprocess.run(['python3' ,'run.py' , '--headless', "--source=./imageRonaldo.jpg", "--target=./video_5s.mp4", "--output=./mp4swapped.mp4" ,"--execution-providers=cuda", "--frame-processors=face_swapper", "--face-swapper-model=inswapper_128_fp16"])
# subprocess.run(['python3' ,'run.py', '--headless', "--source", "./imageRonaldo.jpg", "--target", "./video_5s.mp4", "--output" ,"./mp4swapped.mp4" ,"--execution-providers", "cpu", "--frame-processors", "face_swapper", "--face-swapper-model", "inswapper_128_fp16"])
# subprocess.run(a)
# if platform.system() == "Windows":
#       # Chạy lệnh `dir` trên Windows
#   subprocess.run(["dir"])
# else:
#   # Chạy lệnh `ls` trên các hệ điều hành khác
#   subprocess.run(["ls"])
