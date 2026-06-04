from fastapi import UploadFile, File
import base64 

async def encode_image(upload_file: UploadFile):
    image_bytes = await upload_file.read()
    return base64.b64encode(image_bytes).decode("utf-8")