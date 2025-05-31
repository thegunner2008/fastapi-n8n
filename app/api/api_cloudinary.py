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


@router.get("/crop-image/")
def crop_image(
        image_url: str = Query(..., description="URL ảnh gốc"),
        crop_ratio: float = Query(1.0, gt=0.1, description="Tỷ lệ width/height (ví dụ 1.33 cho 4:3)"),
        output_width: int = Query(800, gt=0, description="Chiều rộng đầu ra (px)")
):
    # Upload ảnh lên Cloudinary
    uploaded = cloudinary.uploader.upload(image_url)
    public_id = uploaded["public_id"]

    # Tính chiều cao dựa trên tỷ lệ crop và chiều rộng yêu cầu
    output_height = int(output_width / crop_ratio)

    # Tạo URL ảnh đã crop bằng AI
    cropped_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=output_width,
        height=output_height,
        crop="fill",         # fill đảm bảo giữ đúng tỉ lệ
        gravity="auto",      # Cloudinary AI chọn vùng cắt thông minh
        format="jpg"
    )

    # Tải ảnh đã xử lý
    response = requests.get(cropped_url)
    if response.status_code != 200:
        return {"error": "Không thể tải ảnh đã crop từ Cloudinary."}

    return StreamingResponse(BytesIO(response.content), media_type="image/jpeg")
