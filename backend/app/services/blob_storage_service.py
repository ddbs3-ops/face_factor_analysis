from uuid import uuid4

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings


ACCOUNT_URL = "https://hairconsultstorage123.blob.core.windows.net"
CONTAINER_NAME = "reference-images"

credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=ACCOUNT_URL,
    credential=credential,
)


def upload_reference_image(
    content: bytes,
    content_type: str,
    extension: str,
) -> str:
    blob_name = f"{uuid4()}{extension}"

    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=blob_name,
    )

    blob_client.upload_blob(
        content,
        overwrite=False,
        content_settings=ContentSettings(
            content_type=content_type,
        ),
    )

    return blob_name