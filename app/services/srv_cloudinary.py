from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import cloudinary
import cloudinary.uploader
import cloudinary.api
from io import BytesIO
import requests


class CloudinaryService(object):
    __instance = None

    def __init__(self) -> None:
        pass
