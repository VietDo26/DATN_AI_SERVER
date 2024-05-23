import os

os.environ['OMP_NUM_THREADS'] = '1'

import signal
import sys
import warnings
import shutil
import numpy
import onnxruntime
from time import sleep, time
from argparse import ArgumentParser, HelpFormatter

import facefusion.choices
import facefusion.globals
from facefusion.face_analyser import get_one_face, get_average_face
from facefusion.face_store import get_reference_faces, append_reference_face
from facefusion import face_analyser, face_masker, content_analyser, config, process_manager, metadata, logger, wording
from facefusion.content_analyser import analyse_image, analyse_video
from facefusion.processors.frame.core import get_frame_processors_modules, load_frame_processor_module
from facefusion.common_helper import create_metavar, get_first
from facefusion.execution import encode_execution_providers, decode_execution_providers
from facefusion.normalizer import normalize_output_path, normalize_padding, normalize_fps
from facefusion.memory import limit_system_memory
from facefusion.statistics import conditional_log_statistics
from facefusion.filesystem import list_directory, get_temp_frame_paths, create_temp, move_temp, clear_temp, is_image, is_video, filter_audio_paths
from facefusion.ffmpeg import extract_frames, merge_video, copy_image, finalize_image, restore_audio, replace_audio
from facefusion.vision import read_image, read_static_images, detect_image_resolution, restrict_video_fps, create_image_resolutions, get_video_frame, detect_video_resolution, detect_video_fps, restrict_video_resolution, restrict_image_resolution, create_video_resolutions, pack_resolution, unpack_resolution

# def apply_args(program : ArgumentParser) -> None:
#     args = program.parse_args()
# 	# general
# 	facefusion.globals.source_paths = args.source_paths
# 	print("facefusion.globals.source_paths =",facefusion.globals.source_paths)
# 	facefusion.globals.target_path = args.target_path
# 	print("facefusion.globals.target_path =",facefusion.globals.target_path)
# 	facefusion.globals.output_path = args.output_path
# 	print("facefusion.globals.output_path =",facefusion.globals.output_path)
# 	# misc
# 	facefusion.globals.skip_download = args.skip_download
# 	print("facefusion.globals.skip_download =",facefusion.globals.skip_download)
# 	facefusion.globals.headless = args.headless
# 	print("facefusion.globals.headless =",facefusion.globals.headless)
# 	facefusion.globals.log_level = args.log_level
# 	print("facefusion.globals.log_level =",facefusion.globals.log_level)
# 	# execution
# 	facefusion.globals.execution_providers = decode_execution_providers(args.execution_providers)
# 	print("facefusion.globals.execution_providers =",facefusion.globals.execution_providers)
# 	facefusion.globals.execution_thread_count = args.execution_thread_count
# 	print("facefusion.globals.execution_thread_count =",facefusion.globals.execution_thread_count)
# 	facefusion.globals.execution_queue_count = args.execution_queue_count
# 	print("facefusion.globals.execution_queue_count =",facefusion.globals.execution_queue_count)
# 	# memory
# 	facefusion.globals.video_memory_strategy = args.video_memory_strategy
# 	print("facefusion.globals.video_memory_strategy =",facefusion.globals.video_memory_strategy)
# 	facefusion.globals.system_memory_limit = args.system_memory_limit
# 	print("facefusion.globals.system_memory_limit =",facefusion.globals.system_memory_limit)
# 	# face analyser
# 	facefusion.globals.face_analyser_order = args.face_analyser_order
# 	print("facefusion.globals.face_analyser_order =",facefusion.globals.face_analyser_order)
# 	facefusion.globals.face_analyser_age = args.face_analyser_age
# 	print("facefusion.globals.face_analyser_age =",facefusion.globals.face_analyser_age)
# 	facefusion.globals.face_analyser_gender = args.face_analyser_gender
# 	print("facefusion.globals.face_analyser_gender =",facefusion.globals.face_analyser_gender)
# 	facefusion.globals.face_detector_model = args.face_detector_model
# 	print("facefusion.globals.face_detector_model =",facefusion.globals.face_detector_model)
# 	if args.face_detector_size in facefusion.choices.face_detector_set[args.face_detector_model]:
# 		facefusion.globals.face_detector_size = args.face_detector_size
# 	else:
# 		facefusion.globals.face_detector_size = '640x640'
# 	print("facefusion.globals.face_detector_size =",facefusion.globals.face_detector_size)
# 	facefusion.globals.face_detector_score = args.face_detector_score
# 	print("facefusion.globals.face_detector_score =",facefusion.globals.face_detector_score)
# 	facefusion.globals.face_landmarker_score = args.face_landmarker_score
# 	print("facefusion.globals.face_landmarker_score =",facefusion.globals.face_landmarker_score )
# 	# face selector
# 	facefusion.globals.face_selector_mode = args.face_selector_mode
# 	print("facefusion.globals.face_selector_mode =",facefusion.globals.face_selector_mode)
# 	facefusion.globals.reference_face_position = args.reference_face_position
# 	print("facefusion.globals.reference_face_position =",facefusion.globals.reference_face_position)
# 	facefusion.globals.reference_face_distance = args.reference_face_distance
# 	print("facefusion.globals.reference_face_distance =",facefusion.globals.reference_face_distance)
# 	facefusion.globals.reference_frame_number = args.reference_frame_number
# 	print("facefusion.globals.reference_frame_number =",facefusion.globals.reference_frame_number)
# 	# face mask
# 	facefusion.globals.face_mask_types = args.face_mask_types
# 	print("facefusion.globals.face_mask_types =",facefusion.globals.face_mask_types)
# 	facefusion.globals.face_mask_blur = args.face_mask_blur
# 	print("facefusion.globals.face_mask_blur =",facefusion.globals.face_mask_blur)
# 	facefusion.globals.face_mask_padding = normalize_padding(args.face_mask_padding)
# 	print("facefusion.globals.face_mask_padding =",facefusion.globals.face_mask_padding)
# 	facefusion.globals.face_mask_regions = args.face_mask_regions
# 	print("facefusion.globals.face_mask_regions =",facefusion.globals.face_mask_regions )
# 	# frame extraction
# 	facefusion.globals.trim_frame_start = args.trim_frame_start
# 	print("facefusion.globals.trim_frame_start =",facefusion.globals.trim_frame_start)
# 	facefusion.globals.trim_frame_end = args.trim_frame_end
# 	print("facefusion.globals.trim_frame_end =",facefusion.globals.trim_frame_end)
# 	facefusion.globals.temp_frame_format = args.temp_frame_format
# 	print("facefusion.globals.temp_frame_format =",facefusion.globals.temp_frame_format)
# 	facefusion.globals.keep_temp = args.keep_temp
# 	print("facefusion.globals.keep_temp =",facefusion.globals.keep_temp)
# 	# output creation
# 	facefusion.globals.output_image_quality = args.output_image_quality
# 	print("facefusion.globals.output_image_quality =",facefusion.globals.output_image_quality)
# 	if is_image(args.target_path):
# 		output_image_resolution = detect_image_resolution(args.target_path)
# 		output_image_resolutions = create_image_resolutions(output_image_resolution)
# 		if args.output_image_resolution in output_image_resolutions:
# 			facefusion.globals.output_image_resolution = args.output_image_resolution
# 		else:
# 			facefusion.globals.output_image_resolution = pack_resolution(output_image_resolution)
# 			print("facefusion.globals.output_image_resolution =",facefusion.globals.output_image_resolution)
# 	facefusion.globals.output_video_encoder = args.output_video_encoder
# 	print("facefusion.globals.output_video_encoder =",facefusion.globals.output_video_encoder)
# 	facefusion.globals.output_video_preset = args.output_video_preset
# 	print("facefusion.globals.output_video_preset =",facefusion.globals.output_video_preset)
# 	facefusion.globals.output_video_quality = args.output_video_quality
# 	print("facefusion.globals.output_video_quality =",facefusion.globals.output_video_quality)
# 	if is_video(args.target_path):
# 		output_video_resolution = detect_video_resolution(args.target_path)
# 		output_video_resolutions = create_video_resolutions(output_video_resolution)
# 		if args.output_video_resolution in output_video_resolutions:
# 			facefusion.globals.output_video_resolution = args.output_video_resolution
# 			print("facefusion.globals.output_video_resolution =",facefusion.globals.output_video_resolution)
# 		else:
# 			facefusion.globals.output_video_resolution = pack_resolution(output_video_resolution)
# 			print("facefusion.globals.output_video_resolution =",facefusion.globals.output_video_resolution)
# 	if args.output_video_fps or is_video(args.target_path):
# 		facefusion.globals.output_video_fps = normalize_fps(args.output_video_fps) or detect_video_fps(args.target_path)
# 		print("facefusion.globals.output_video_fps =",facefusion.globals.output_video_fps)
# 	facefusion.globals.skip_audio = args.skip_audio
# 	print("facefusion.globals.skip_audio =",facefusion.globals.skip_audio)
# 	# frame processors
# 	available_frame_processors = list_directory('facefusion/processors/frame/modules')
# 	facefusion.globals.frame_processors = args.frame_processors
# 	print("facefusion.globals.frame_processors =",facefusion.globals.frame_processors)
# 	for frame_processor in available_frame_processors:
# 		frame_processor_module = load_frame_processor_module(frame_processor)
# 		frame_processor_module.apply_args(program)
# 	# uis
# 	facefusion.globals.ui_layouts = args.ui_layouts

def pre_check() -> bool:
    if sys.version_info < (3, 9):
        logger.error(wording.get('python_not_supported').format(version = '3.9'), __name__.upper())
        return False
    if not shutil.which('ffmpeg'):
        logger.error(wording.get('ffmpeg_not_installed'), __name__.upper())
        return False
    return True

def conditional_process() -> None:
	start_time = time()
	for frame_processor_module in get_frame_processors_modules(facefusion.globals.frame_processors):
		while not frame_processor_module.post_check():
			logger.disable()
			sleep(0.5)
		logger.enable()
		if not frame_processor_module.pre_process('output'):
			return
	conditional_append_reference_faces()
	if is_image(facefusion.globals.target_path):
		process_image(start_time)
	if is_video(facefusion.globals.target_path):
		process_video(start_time)

def conditional_append_reference_faces() -> None:
    if 'reference' in facefusion.globals.face_selector_mode and not get_reference_faces():
        source_frames = read_static_images(facefusion.globals.source_paths)
        source_face = get_average_face(source_frames)
        if is_video(facefusion.globals.target_path):
            reference_frame = get_video_frame(facefusion.globals.target_path, facefusion.globals.reference_frame_number)
        else:
            reference_frame = read_image(facefusion.globals.target_path)
        reference_face = get_one_face(reference_frame, facefusion.globals.reference_face_position)
        append_reference_face('origin', reference_face)
        if source_face and reference_face:
            for frame_processor_module in get_frame_processors_modules(facefusion.globals.frame_processors):
                abstract_reference_frame = frame_processor_module.get_reference_frame(source_face, reference_face, reference_frame)
                if numpy.any(abstract_reference_frame):
                    reference_frame = abstract_reference_frame
                    reference_face = get_one_face(reference_frame, facefusion.globals.reference_face_position)
                    append_reference_face(frame_processor_module.__name__, reference_face)

def process_image(start_time : float) -> None:
	normed_output_path = normalize_output_path(facefusion.globals.target_path, facefusion.globals.output_path)
	if analyse_image(facefusion.globals.target_path):
		return
	# copy image
	process_manager.start()
	temp_image_resolution = pack_resolution(restrict_image_resolution(facefusion.globals.target_path, unpack_resolution(facefusion.globals.output_image_resolution)))
	logger.info(wording.get('copying_image').format(resolution = temp_image_resolution), __name__.upper())
	if copy_image(facefusion.globals.target_path, normed_output_path, temp_image_resolution):
		logger.debug(wording.get('copying_image_succeed'), __name__.upper())
	else:
		logger.error(wording.get('copying_image_failed'), __name__.upper())
		return
	# process image
	for frame_processor_module in get_frame_processors_modules(facefusion.globals.frame_processors):
		logger.info(wording.get('processing'), frame_processor_module.NAME)
		frame_processor_module.process_image(facefusion.globals.source_paths, normed_output_path, normed_output_path)
		frame_processor_module.post_process()
	if is_process_stopping():
		return
	# finalize image
	logger.info(wording.get('finalizing_image').format(resolution = facefusion.globals.output_image_resolution), __name__.upper())
	if finalize_image(normed_output_path, facefusion.globals.output_image_resolution):
		logger.debug(wording.get('finalizing_image_succeed'), __name__.upper())
	else:
		logger.warn(wording.get('finalizing_image_skipped'), __name__.upper())
	# validate image
	if is_image(normed_output_path):
		seconds = '{:.2f}'.format((time() - start_time) % 60)
		logger.info(wording.get('processing_image_succeed').format(seconds = seconds), __name__.upper())
		conditional_log_statistics()
	else:
		logger.error(wording.get('processing_image_failed'), __name__.upper())
	process_manager.end()


def is_process_stopping() -> bool:
	if process_manager.is_stopping():
		process_manager.end()
		logger.info(wording.get('processing_stopped'), __name__.upper())
	return process_manager.is_pending()


def process_video(start_time : float) -> None:
	normed_output_path = normalize_output_path(facefusion.globals.target_path, facefusion.globals.output_path)
	if analyse_video(facefusion.globals.target_path, facefusion.globals.trim_frame_start, facefusion.globals.trim_frame_end):
		return
	# clear temp
	logger.debug(wording.get('clearing_temp'), __name__.upper())
	clear_temp(facefusion.globals.target_path)
	# create temp
	logger.debug(wording.get('creating_temp'), __name__.upper())
	create_temp(facefusion.globals.target_path)
	# extract frames
	process_manager.start()
	temp_video_resolution = pack_resolution(restrict_video_resolution(facefusion.globals.target_path, unpack_resolution(facefusion.globals.output_video_resolution)))
	temp_video_fps = restrict_video_fps(facefusion.globals.target_path, facefusion.globals.output_video_fps)
	logger.info(wording.get('extracting_frames').format(resolution = temp_video_resolution, fps = temp_video_fps), __name__.upper())
	if extract_frames(facefusion.globals.target_path, temp_video_resolution, temp_video_fps):
		logger.debug(wording.get('extracting_frames_succeed'), __name__.upper())
	else:
		if is_process_stopping():
			return
		logger.error(wording.get('extracting_frames_failed'), __name__.upper())
		return
	# process frames
	temp_frame_paths = get_temp_frame_paths(facefusion.globals.target_path)
	if temp_frame_paths:
		for frame_processor_module in get_frame_processors_modules(facefusion.globals.frame_processors):
			logger.info(wording.get('processing'), frame_processor_module.NAME)
			frame_processor_module.process_video(facefusion.globals.source_paths, temp_frame_paths)
			frame_processor_module.post_process()
		if is_process_stopping():
			return
	else:
		logger.error(wording.get('temp_frames_not_found'), __name__.upper())
		return
	# merge video
	logger.info(wording.get('merging_video').format(resolution = facefusion.globals.output_video_resolution, fps = facefusion.globals.output_video_fps), __name__.upper())
	if merge_video(facefusion.globals.target_path, facefusion.globals.output_video_resolution, facefusion.globals.output_video_fps):
		logger.debug(wording.get('merging_video_succeed'), __name__.upper())
	else:
		if is_process_stopping():
			return
		logger.error(wording.get('merging_video_failed'), __name__.upper())
		return
	# handle audio
	if facefusion.globals.skip_audio:
		logger.info(wording.get('skipping_audio'), __name__.upper())
		move_temp(facefusion.globals.target_path, normed_output_path)
	else:
		if 'lip_syncer' in facefusion.globals.frame_processors:
			source_audio_path = get_first(filter_audio_paths(facefusion.globals.source_paths))
			if source_audio_path and replace_audio(facefusion.globals.target_path, source_audio_path, normed_output_path):
				logger.debug(wording.get('restoring_audio_succeed'), __name__.upper())
			else:
				if is_process_stopping():
					return
				logger.warn(wording.get('restoring_audio_skipped'), __name__.upper())
				move_temp(facefusion.globals.target_path, normed_output_path)
		else:
			if restore_audio(facefusion.globals.target_path, normed_output_path, facefusion.globals.output_video_fps):
				logger.debug(wording.get('restoring_audio_succeed'), __name__.upper())
			else:
				if is_process_stopping():
					return
				logger.warn(wording.get('restoring_audio_skipped'), __name__.upper())
				move_temp(facefusion.globals.target_path, normed_output_path)
	# clear temp
	logger.debug(wording.get('clearing_temp'), __name__.upper())
	clear_temp(facefusion.globals.target_path)
	# validate video
	if is_video(normed_output_path):
		seconds = '{:.2f}'.format((time() - start_time))
		logger.info(wording.get('processing_video_succeed').format(seconds = seconds), __name__.upper())
		conditional_log_statistics()
	else:
		logger.error(wording.get('processing_video_failed'), __name__.upper())
	process_manager.end()

def set_attributes(source_paths:list,
                   target_path: str,
                   output_path: str,
                   skip_download: bool = None,
                   headless: bool = True,
                   log_level: str = 'info',
                   execution_providers: list =['cpu'],
                   execution_thread_count:int = 4,
                   execution_queue_count: int =1,
                   video_memory_strategy: str ='strict',
                   system_memory_limit: int =0,
                   face_analyser_order: str = 'face_analyser_order',
                   face_analyser_age: str = None,
                   face_analyser_gender: str = 'male',
                   face_detector_model: str ='yoloface',
                   face_detector_size: str = '640x640',
                   face_detector_score: float = 0.7,
                   face_landmarker_score: float = 0.5,
                   face_selector_mode: str = 'reference',
                   reference_face_position: int =0,
                   reference_face_distance: float = 0.8,
                   reference_frame_number: int=100,
                   face_mask_types : str = 'box',
                   face_mask_blur: float = 0.6,
                   face_mask_padding: list = [0, 0, 0, 0],
                   face_mask_regions: list =['skin', 'left-eyebrow', 'right-eyebrow', 'left-eye', 'right-eye', 'eye-glasses', 'nose', 'mouth', 'upper-lip', 'lower-lip'],
                   trim_frame_start: int = None,
                   trim_frame_end: int = None,
                   temp_frame_format: str = 'png',
                   keep_temp: bool = True,
                   output_image_quality: int = 100,
                   args_output_image_resolution: str = None,
                   output_video_encoder: str = 'libx264',
                   output_video_preset: str = 'ultrafast',
                   output_video_quality: int = 100,
                   args_output_video_resolution : str= None,
                   args_output_video_fps : float = None,
                   skip_audio: bool = None,
                   frame_processors : list = ['face_swapper'],
                   ui_layouts : list = ['default']
                   ):
	facefusion.globals.source_paths = source_paths
	print("facefusion.globals.source_paths =",facefusion.globals.source_paths)
	facefusion.globals.target_path = target_path
	print("facefusion.globals.target_path =",facefusion.globals.target_path)
	facefusion.globals.output_path = output_path
	print("facefusion.globals.output_path =",facefusion.globals.output_path)
	# misc
	facefusion.globals.skip_download = skip_download
	print("facefusion.globals.skip_download =",facefusion.globals.skip_download)
	facefusion.globals.headless = headless
	print("facefusion.globals.headless =",facefusion.globals.headless)
	facefusion.globals.log_level = log_level
	print("facefusion.globals.log_level =",facefusion.globals.log_level)
	# execution
	facefusion.globals.execution_providers = decode_execution_providers(execution_providers)
	print("facefusion.globals.execution_providers =",facefusion.globals.execution_providers)
	facefusion.globals.execution_thread_count = execution_thread_count
	print("facefusion.globals.execution_thread_count =",facefusion.globals.execution_thread_count)
	facefusion.globals.execution_queue_count = execution_queue_count
	print("facefusion.globals.execution_queue_count =",facefusion.globals.execution_queue_count)
	# memory
	facefusion.globals.video_memory_strategy = video_memory_strategy
	print("facefusion.globals.video_memory_strategy =",facefusion.globals.video_memory_strategy)
	facefusion.globals.system_memory_limit = system_memory_limit
	print("facefusion.globals.system_memory_limit =",facefusion.globals.system_memory_limit)
	# face analyser
	facefusion.globals.face_analyser_order = face_analyser_order
	print("facefusion.globals.face_analyser_order =",facefusion.globals.face_analyser_order)
	facefusion.globals.face_analyser_age = face_analyser_age
	print("facefusion.globals.face_analyser_age =",facefusion.globals.face_analyser_age)
	facefusion.globals.face_analyser_gender = face_analyser_gender
	print("facefusion.globals.face_analyser_gender =",facefusion.globals.face_analyser_gender)
    # ['many', 'retinaface', 'scrfd', 'yoloface', 'yunet']
	facefusion.globals.face_detector_model = face_detector_model
	print("facefusion.globals.face_detector_model =",facefusion.globals.face_detector_model)
	facefusion.globals.face_detector_size = face_detector_size
	print("facefusion.globals.face_detector_size =",facefusion.globals.face_detector_size)
	facefusion.globals.face_detector_score = face_detector_score
	print("facefusion.globals.face_detector_score =",facefusion.globals.face_detector_score)
	facefusion.globals.face_landmarker_score = face_landmarker_score
	print("facefusion.globals.face_landmarker_score =",facefusion.globals.face_landmarker_score )
	# face selector ['many', 'one', 'reference']
	facefusion.globals.face_selector_mode = face_selector_mode
	print("facefusion.globals.face_selector_mode =",facefusion.globals.face_selector_mode)
	facefusion.globals.reference_face_position = reference_face_position
	print("facefusion.globals.reference_face_position =",facefusion.globals.reference_face_position)
	facefusion.globals.reference_face_distance = reference_face_distance
	print("facefusion.globals.reference_face_distance =",facefusion.globals.reference_face_distance)
	facefusion.globals.reference_frame_number = reference_frame_number
	print("facefusion.globals.reference_frame_number =",facefusion.globals.reference_frame_number)
	# face mask
    # box//occlusion//region
	facefusion.globals.face_mask_types = face_mask_types
	print("facefusion.globals.face_mask_types =",facefusion.globals.face_mask_types)
	facefusion.globals.face_mask_blur = face_mask_blur
	print("facefusion.globals.face_mask_blur =",facefusion.globals.face_mask_blur)
	facefusion.globals.face_mask_padding = normalize_padding(face_mask_padding)
	print("facefusion.globals.face_mask_padding =",facefusion.globals.face_mask_padding)
	facefusion.globals.face_mask_regions = face_mask_regions
	print("facefusion.globals.face_mask_regions =",facefusion.globals.face_mask_regions )
	# frame extraction
	facefusion.globals.trim_frame_start = trim_frame_start
	print("facefusion.globals.trim_frame_start =",facefusion.globals.trim_frame_start)
	facefusion.globals.trim_frame_end = trim_frame_end
	print("facefusion.globals.trim_frame_end =",facefusion.globals.trim_frame_end)
	facefusion.globals.temp_frame_format = temp_frame_format
	print("facefusion.globals.temp_frame_format =",facefusion.globals.temp_frame_format)
	facefusion.globals.keep_temp = keep_temp
	print("facefusion.globals.keep_temp =",facefusion.globals.keep_temp)
	# output creation
	facefusion.globals.output_image_quality = output_image_quality
	print("facefusion.globals.output_image_quality =",facefusion.globals.output_image_quality)
	if is_image(target_path):
		output_image_resolution = detect_image_resolution(target_path)
		output_image_resolutions = create_image_resolutions(output_image_resolution)
		if args_output_image_resolution in output_image_resolutions:
			facefusion.globals.output_image_resolution = args_output_image_resolution
		else:
			facefusion.globals.output_image_resolution = pack_resolution(output_image_resolution)
			print("facefusion.globals.output_image_resolution =",facefusion.globals.output_image_resolution)
	facefusion.globals.output_video_encoder = output_video_encoder
	print("facefusion.globals.output_video_encoder =",facefusion.globals.output_video_encoder)
    # output_video_encoder : ultrafast/superfast/veryfast/faster/fast/medium/slow/slower/veryslow
	facefusion.globals.output_video_preset = output_video_preset
	print("facefusion.globals.output_video_preset =",facefusion.globals.output_video_preset)
	facefusion.globals.output_video_quality = output_video_quality
	print("facefusion.globals.output_video_quality =",facefusion.globals.output_video_quality)
	if is_video(target_path):
		output_video_resolution = detect_video_resolution(target_path)
		output_video_resolutions = create_video_resolutions(output_video_resolution)
		if args_output_video_resolution in output_video_resolutions:
			facefusion.globals.output_video_resolution = args_output_video_resolution
			print("facefusion.globals.output_video_resolution =",facefusion.globals.output_video_resolution)
		else:
			facefusion.globals.output_video_resolution = pack_resolution(output_video_resolution)
			print("facefusion.globals.output_video_resolution =",facefusion.globals.output_video_resolution)
	if args_output_video_fps or is_video(target_path):
		facefusion.globals.output_video_fps = normalize_fps(args_output_video_fps) or detect_video_fps(target_path)
		print("facefusion.globals.output_video_fps =",facefusion.globals.output_video_fps)
	facefusion.globals.skip_audio = skip_audio
	print("facefusion.globals.skip_audio =",facefusion.globals.skip_audio)
	# frame processors
	available_frame_processors = ['face_debugger', 'face_enhancer', 'face_swapper', 'frame_enhancer', 'lip_syncer']
	facefusion.globals.frame_processors = frame_processors
	print("facefusion.globals.frame_processors =",facefusion.globals.frame_processors)
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		print(frame_processor_module)
		# frame_processor_module.set_attributes()
		# frame_processor_module.apply_args(program)
	# uis
	facefusion.globals.ui_layouts = ui_layouts

def run():
	set_attributes(source_paths=['./imageRonaldo.jpg'],target_path='./video_5s.mp4',output_path='./test.mp4')
	logger.init(facefusion.globals.log_level)
	facefusion.globals.system_memory_limit = 0
	facefusion.globals.frame_processors = ['face_swapper']
	if facefusion.globals.system_memory_limit > 0:
		limit_system_memory(facefusion.globals.system_memory_limit)
	if not pre_check() or not content_analyser.pre_check() or not face_analyser.pre_check() or not face_masker.pre_check():
		return

	for frame_processor_module in get_frame_processors_modules(facefusion.globals.frame_processors):
		if not frame_processor_module.pre_check():
			return
	conditional_process()

# if __name__ == '__main__':
#     run()
