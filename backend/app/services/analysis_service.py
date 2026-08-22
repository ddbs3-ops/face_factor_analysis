import os
import tempfile

from fastapi import UploadFile

from analyze_user import analyze_user_image


async def analyze_uploaded_image(file: UploadFile):
    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        result = analyze_user_image(temp_path)

        if result is None:
            return None

        return {
            "rules": result["rules"],
            "merged_adjustments": result["merged_adjustments"],
            "recommendations": result["recommendations"],
        }

    finally:
        os.remove(temp_path)
