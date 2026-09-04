from pathlib import Path

from backend.app.services.blob_storage_service import (
    upload_reference_image,
)


IMAGE_PATH = Path("test.png")

with IMAGE_PATH.open("rb") as file:
    content = file.read()

blob_name = upload_reference_image(
    content=content,
    content_type="image/png",
    extension=".png",
)

print("uploaded:", blob_name)