import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import sys
import os
from pathlib import Path
import datetime
import subprocess

from fastapi import APIRouter
from PIL import Image
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse,  FileResponse, JSONResponse
from database.database import insert_data_into_database
from utils.videoprocessing.concatenate import concatenateWarning

folder_path= str(Path(__file__).parent.parent)


router = APIRouter()

@router.post("/convertvideo/")
async def convertvideo( user_id:int,
                       image: UploadFile = File(...),
                       video: UploadFile = File(...)
                       ):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads allowed!")

    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video uploads allowed!")

    upload_dir_media = os.path.join(folder_path,'media',f'user_id_{user_id:04d}')
    if not os.path.exists(upload_dir_media):
        os.makedirs(upload_dir_media)
    number_order = len(os.listdir(upload_dir_media))
    upload_dir_media = os.path.join(upload_dir_media,f'{number_order:05d}')
    print(upload_dir_media)
    if not os.path.exists(upload_dir_media):
        os.makedirs(upload_dir_media)

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    print(upload_dir_media)
    index_image = image.filename.rfind('.')
    file_path_image=upload_dir_media+f'/image_{user_id:04d}_{number_order:05d}'+image.filename[index_image:]

    try:
        pil_img = Image.open(image.file)
        pil_img.save(file_path_image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")

    index_video = video.filename.rfind('.')
    file_path_video=upload_dir_media+f'/targetvideo_{user_id:04d}_{number_order:05d}'+video.filename[index_video:]
    try:
        with open( file_path_video, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

    try:
        output = upload_dir_media + f'/processedvideo_{user_id:04d}_{number_order:05d}'+video.filename[index_video:]
        print('output :', output)
        subprocess.run(['python3' ,'run.py' , '--headless', f'--source={file_path_image}', f"--target={file_path_video}", f"--output={output}" ,"--execution-providers=cpu", "--frame-processors=face_swapper", "--face-swapper-model=inswapper_128_fp16"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Faild to convert video {e}')
    # insert_data_into_database()
    output_final = upload_dir_media + f'/processedvideo_{user_id:04d}_{number_order:05d}_final'+video.filename[index_video:]
    concatenateWarning(video_path=output,output_path= output_final)
    print('output_final',output_final)
    link_url = f'/convertfile/filevideo/?path={output_final}'
    return JSONResponse(content = link_url)
    # return RedirectResponse(link_url)

@router.get("/filevideo/")
async def filevideo(path: str):
    return FileResponse(path)

@router.get("/testconnect/")
async def testconnect():
    return JSONResponse(content = "connect succes")
