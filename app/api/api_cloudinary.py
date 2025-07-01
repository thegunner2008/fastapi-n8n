import re

from fastapi import Query, APIRouter
from fastapi.responses import StreamingResponse
import cloudinary
import cloudinary.uploader
import cloudinary.api
from io import BytesIO
import requests

router = APIRouter()

cloudinary.config(
    cloud_name="detnaszuk",
    api_key="678573656883669",
    api_secret="bnu_XlOW_ThpAnaEuSw0Ozq9sWM",
    secure=True
)


@router.get("/scale-image")
def scale_image(
        image_url: str = Query(..., description="URL ảnh gốc"),
        scale: float = Query(1.0, gt=0.0, description="Tỷ lệ scale, ví dụ 0.5 để giảm 50%"),
):
    # Upload ảnh tạm lên Cloudinary (nếu là ảnh từ URL ngoài)
    uploaded = cloudinary.uploader.upload(image_url)

    public_id = uploaded["public_id"]
    width = uploaded.get("width")
    height = uploaded.get("height")

    if not width or not height:
        return {"error": "Không thể lấy kích thước ảnh gốc."}

    new_width = int(width * scale)
    new_height = int(height * scale)

    # Tạo URL với transformation scale
    scaled_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=new_width,
        height=new_height,
        crop="scale",
        format="jpg"
    )

    # Tải ảnh đã scale về và trả về dưới dạng file
    response = requests.get(scaled_url)
    if response.status_code != 200:
        return {"error": "Không thể tải ảnh đã scale từ Cloudinary."}

    return StreamingResponse(BytesIO(response.content), media_type="image/jpeg")


def convert_drive_url(image_url: str) -> str:
    match = re.match(r"https://drive\.google\.com/file/d/([^/]+)/view", image_url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return image_url


@router.get("/crop-image")
def crop_image(
        image_url: str = Query(..., description="URL ảnh gốc"),
        output_width: int = Query(..., gt=0, description="Chiều rộng đầu ra (px)"),
        output_height: int = Query(..., gt=0, description="Chiều cao đầu ra (px)"),
        auto_scale: bool = Query(True, description="Tự động scale theo chiều lớn hơn để giữ tỷ lệ"),
        output_is_url: bool = Query(True, description="Trả về URL của ảnh đã crop thay vì file ảnh trực tiếp")
):
    image_url = convert_drive_url(image_url)

    # Upload ảnh lên Cloudinary
    uploaded = cloudinary.uploader.upload(image_url)
    public_id = uploaded["public_id"]

    # Tính tỷ lệ crop
    crop_ratio = output_width / output_height

    # Nếu auto_scale = True, scale theo chiều lớn hơn
    if auto_scale:
        original_width = uploaded.get("width")
        original_height = uploaded.get("height")
        original_ratio = original_width / original_height if original_height else crop_ratio

        if original_ratio == crop_ratio:
            output_width = int(original_width)
            output_height = int(original_height)
        elif original_ratio < crop_ratio:
            output_height = int(original_width / crop_ratio)
            output_width = int(original_width)
        else:
            output_width = int(original_height * crop_ratio)
            output_height = int(original_height)

    # Tạo URL ảnh đã crop bằng AI
    cropped_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=output_width,
        height=output_height,
        crop="fill",
        gravity="auto",
        format="jpg"
    )

    if output_is_url:
        return {"image_url": cropped_url}

    # Tải ảnh đã xử lý
    response = requests.get(cropped_url)
    if response.status_code != 200:
        return {"error": f"{response}"}

    return StreamingResponse(BytesIO(response.content), media_type="image/jpeg")

@router.get("/fill-image")
def fill_image(
        image_url: str = Query(..., description="URL ảnh gốc"),
        output_width: int = Query(..., gt=0, description="Chiều rộng đầu ra (px)"),
        output_height: int = Query(..., gt=0, description="Chiều cao đầu ra (px)"),
        auto_scale: bool = Query(True, description="Tự động scale theo chiều lớn hơn để giữ tỷ lệ"),
        output_is_url: bool = Query(True, description="Trả về URL của ảnh đã crop thay vì file ảnh trực tiếp")
):
    image_url = convert_drive_url(image_url)

    # Upload ảnh lên Cloudinary
    uploaded = cloudinary.uploader.upload(image_url)
    public_id = uploaded["public_id"]

    # Tính tỷ lệ crop
    crop_ratio = output_width / output_height

    # Nếu auto_scale = True, scale theo chiều lớn hơn
    if auto_scale:
        original_width = uploaded.get("width")
        original_height = uploaded.get("height")
        original_ratio = original_width / original_height if original_height else crop_ratio

        if original_ratio == crop_ratio:
            return {"image_url": image_url}
        else:
            output_width = int(original_height * crop_ratio)
            if output_width < original_width:
                output_width = original_width

    # Tạo URL ảnh đã crop bằng AI
    cropped_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=output_width,
        crop="pad",
        aspect_ratio=f"{crop_ratio}",
        background="gen_fill",
        quality="auto",
        fetch_format="auto",
        format="jpg"
    )

    if output_is_url:
        return {"image_url": cropped_url}

    # Tải ảnh đã xử lý
    response = requests.get(cropped_url)
    if response.status_code != 200:
        return {"error": f"{response}"}

    return StreamingResponse(BytesIO(response.content), media_type="image/jpeg")
