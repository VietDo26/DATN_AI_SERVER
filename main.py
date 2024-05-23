# from typing import Annotated
# import sys
# import os
# from pathlib import Path
# import datetime
# import platform
# import subprocess
# import signal

# from PIL import Image
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse,  FileResponse
# from database.database import insert_data_into_database
# folder_path= str(Path(__file__).parent)

# # os.path.dirname() to parent folder
# sys.path.append(folder_path)

# app = FastAPI()


# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}


# app = FastAPI()


# @app.get("/filevideo/")
# async def filevideo(path: str):
#     return FileResponse(path)
# # ?skip=0&limit=10
# @app.get("/test/")
# async def testURL():
#     # return filevideo()
#     file_path = '/home/viet/workspace/facefusion/video.mp4'
#     link_url = f'/filevideo/?path={file_path}'
#     return RedirectResponse(link_url)

# # @app.get("/streamvideo")
# # def main():
# #     some_file_path = '/home/viet/workspace/facefusion/video.mp4'
# #     def iterfile():  #
# #         with open(some_file_path, mode="rb") as file_like:  #
# #             yield from file_like  #

# #     return StreamingResponse(iterfile(), media_type="video/mp4")

# # @app.get("/items/")
# # async def read_items():
# #     html_content = """
# #     <html>
# #         <head>
# #             <title>Some HTML in here</title>
# #         </head>
# #         <body>
# #             <h1>Look ma! HTML!</h1>
# #         </body>
# #     </html>
# #     """
# #     return HTMLResponse(content=html_content, status_code=200)

# @app.get("/fastapi", response_class=RedirectResponse)
# async def redirect_response():
#     return "https://fastapi.tiangolo.com"

# @app.post("/uploadimage/")
# async def create_file(
#                       image: UploadFile = File(...)
#                       ):
#     if not image.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Only image uploads allowed!")
#     upload_dir = 'images'
#     if not os.path.exists(upload_dir):
#         os.makedirs(upload_dir)

#     file_path=os.getcwd()+"/images/"+image.filename.replace(" ","-")
#     print(file_path)
#     index = image.filename.rfind('.')
#     try:
#         pil_img = Image.open(image.file)
#         pil_img.save(file_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")
#     return {
#         "message": "Image uploaded successfully!",
#         "filename": file_path,
#         "filename_origin": image.filename[index:]
#         }
# @app.post("/uploadvideo/")
# async def create_file(
#                       video: UploadFile = File(...)
#                       ):
#     # Check if a file is uploaded
#     if not video.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Only video uploads allowed!")

#     filename = video.filename
#     print(filename)
#     upload_dir= "videos"
#     if not os.path.exists(upload_dir):
#         os.makedirs(upload_dir)


#     file_path=os.getcwd()+"/videos/"+video.filename.replace(" ","-")
#     print(file_path)
#     try:
#         with open(os.path.join(upload_dir, filename), "wb") as buffer:
#             content = await video.read()
#             buffer.write(content)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")


#     return {
#         "message": "Video uploaded successfully!"
#         # "filename": file_path
#         }


# @app.post("/convertvideo/")
# async def convertvideo( user_id:int,
#                        image: UploadFile = File(...),
#                        video: UploadFile = File(...)
#                        ):
#     if not image.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="Only image uploads allowed!")

#     if not video.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Only video uploads allowed!")

#     upload_dir_media = os.path.join(folder_path,'media',f'user_id_{user_id:04d}')
#     if not os.path.exists(upload_dir_media):
#         os.makedirs(upload_dir_media)
#     number_order = len(os.listdir(upload_dir_media))
#     upload_dir_media = os.path.join(upload_dir_media,f'{number_order:05d}')
#     print(upload_dir_media)
#     if not os.path.exists(upload_dir_media):
#         os.makedirs(upload_dir_media)

#     now = datetime.datetime.now()
#     timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
#     print(upload_dir_media)
#     index_image = image.filename.rfind('.')
#     file_path_image=upload_dir_media+f'/image_{user_id:04d}_{number_order:05d}'+image.filename[index_image:]

#     try:
#         pil_img = Image.open(image.file)
#         pil_img.save(file_path_image)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")

#     index_video = video.filename.rfind('.')
#     file_path_video=upload_dir_media+f'/targetvideo_{user_id:04d}_{number_order:05d}'+video.filename[index_video:]
#     try:
#         with open( file_path_video, "wb") as buffer:
#             content = await video.read()
#             buffer.write(content)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

#     try:
#         output = upload_dir_media + f'/processedvideo_{user_id:04d}_{number_order:05d}'+video.filename[index_video:]
#         print(output)
#         # subprocess.run(['python3' ,'run.py' , '--headless', f'--source={file_path_image}', f"--target={file_path_video}", f"--output={output}" ,"--execution-providers=cpu", "--frame-processors=face_swapper", "--face-swapper-model=inswapper_128_fp16"])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f'Faild to convert video {e}')
#     # insert_data_into_database()
#     link_url = f'/filevideo/?path={output}'
#     return RedirectResponse(link_url)

from typing import Union

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()


class Invoice(BaseModel):
    id: str
    title: Union[str, None] = None
    customer: str
    total: float


class InvoiceEvent(BaseModel):
    description: str
    paid: bool


class InvoiceEventReceived(BaseModel):
    ok: bool


invoices_callback_router = APIRouter()


@invoices_callback_router.post(
    "{$callback_url}/invoices/{$request.body.id}", response_model=InvoiceEventReceived
)
def invoice_notification(body: InvoiceEvent):
    pass


@app.post("/invoices/", callbacks=invoices_callback_router.routes)
def create_invoice(invoice: Invoice, callback_url: Union[HttpUrl, None] = None):
    """
    Create an invoice.

    This will (let's imagine) let the API user (some external developer) create an
    invoice.

    And this path operation will:

    * Send the invoice to the client.
    * Collect the money from the client.
    * Send a notification back to the API user (the external developer), as a callback.
        * At this point is that the API will somehow send a POST request to the
            external API with the notification of the invoice event
            (e.g. "payment successful").
    """
    # Send the invoice, collect the money, send the notification (the callback)
    return {"msg": "Invoice received"}
