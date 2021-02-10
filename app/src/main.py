import io
import shutil
import uuid
from os import path, listdir
from os.path import isfile, join
from typing import Union, List, Dict, AnyStr, Any

import uncurl as uncurl
from PIL import Image
from fastapi import File, Form, UploadFile
from loguru import logger as app_logger
from starlette.responses import FileResponse
from src.fastAPI_utils import create_app

from src.responseModels import AlgorithmResponse, LouvRequest

global last_file_full_path
global files_names

files_folder = './resources/'

rest_app = create_app()


# For Doron:
# Parse the Body as json + query_params args:
@rest_app.post("/insertVector", tags=["LeLouv"])
async def insert_vector(gallery: str,
                        algo_response: AlgorithmResponse):
    app_logger.info(gallery)
    app_logger.info(algo_response)
    return algo_response


# Create new object of this specific request in this case its the collection name:
@rest_app.post("/insertVectorSingleJson", tags=["LeLouv"])
async def insert_vector_form(louv_request: LouvRequest):
    app_logger.info(louv_request)
    return louv_request


# Parse json yourself:
JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


@rest_app.post("/insertVectorParseYourSelf", tags=["LeLouv"])
async def insert_vector_parse_yourself(arbitrary_json: JSONStructure = None):
    return {"received_data": arbitrary_json}


@rest_app.post("/curl2python", tags=["rest_utils"])
async def curl2python(curl_request: str = Form(...)):
    app_logger.info(f"curl: {curl_request}")
    python_code = uncurl.parse(curl_request)
    app_logger.info(f"requests: {python_code}")
    return python_code


# Files Server:
@rest_app.post("/saveImage", tags=["Images"])
async def receive_and_parse_json(image_id: str = Form(""),
                                 image: UploadFile = File(...)):
    contents = await image.read()
    pil_img, json_result = extract_image_metadata(contents)
    if image_id == "":
        file_name = f"{uuid.uuid4()}.{json_result['imageType']}"
    else:
        file_name = f"{image_id}.{json_result['imageType']}"
    json_result['imageId'] = file_name

    if path.exists(json_result['imageId']):
        raise Exception("image with that name exist")
    pil_img.save(f'{files_folder}/{file_name}')
    app_logger.info("\nUploaded image:\n" + "\n".join(f"{k}: {v}" for k, v in json_result.items()))
    update_files_list()
    return json_result


@rest_app.post("/saveImage", tags=["Files"])
async def save_image(image_id: str = Form(""),
                     image: UploadFile = File(...)):
    contents = await image.read()
    pil_img, json_result = extract_image_metadata(contents)
    if image_id == "":
        file_name = f"{uuid.uuid4()}.{json_result['imageType']}"
    else:
        file_name = f"{image_id}.{json_result['imageType']}"
    json_result['imageId'] = file_name

    if path.exists(json_result['imageId']):
        raise Exception("image with that name exist")
    pil_img.save(f'{files_folder}/{file_name}')
    app_logger.info("\nUploaded image:\n" + "\n".join(f"{k}: {v}" for k, v in json_result.items()))
    update_files_list()
    return json_result


@rest_app.get("/getFile/{file_name}", tags=["Files"])
async def get_file(file_name: str):
    file_full_path = f'{files_folder}{file_name}'
    app_logger.info(f"looking for: {file_full_path}")
    global last_file_full_path
    last_file_full_path = file_full_path
    app_logger.info(f"Sending back file: {file_full_path}")
    return FileResponse(file_full_path)


@rest_app.get("/getLastServedFile", tags=["Files"])
async def get_last_served_file():
    app_logger.info(f"lastFile: {last_file_full_path}")
    return FileResponse(last_file_full_path)


@rest_app.get("/getFilesInfo", tags=["Files"])
async def get_files_info():
    total, used, free = shutil.disk_usage(files_folder)
    info = {"files": files_names,
            "total": f"{(total // (2 ** 30))} GiB",
            "used": f"{(used // (2 ** 30))} GiB",
            "free": f"{(free // (2 ** 30))} GiB"}
    app_logger.info(info)
    return info


def update_files_list():
    global files_names
    files_names = [file for file in listdir(files_folder) if isfile(join(files_folder, file))]
    app_logger.info("\nFiles:\n" + "\n".join(f"{file}" for file in files_names))


def extract_image_metadata(img_bytes):
    pil_img = Image.open(io.BytesIO(img_bytes))
    img_type = pil_img.format
    img_width = pil_img.size[0]
    img_height = pil_img.size[1]
    img_size_kb = round(len(img_bytes) / 1024, 2)
    pixels_amount = img_height * img_width
    return pil_img, {'imageType': img_type,
                     'imageSizeKB': img_size_kb,
                     'imageWidth': img_width,
                     'imageHeight': img_height,
                     'pixelsAmount': pixels_amount}


update_files_list()
last_file_full_path = files_folder + files_names[0]
app_logger.info(f"last file: {last_file_full_path}")
