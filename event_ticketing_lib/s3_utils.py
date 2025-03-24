import boto3
import uuid

s3 = boto3.client('s3', region_name='eu-west-1')

BUCKET_NAME = 'event-ticketing-media-anuj-9821'  # ← Use your actual bucket name

def upload_file_to_s3(file_obj, filename_prefix='event'):
    unique_filename = f"{filename_prefix}_{uuid.uuid4()}.pdf"

    # ✅ Proper indentation here
    s3.upload_fileobj(
        Fileobj=file_obj,
        Bucket=BUCKET_NAME,
        Key=unique_filename
    )

    file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
    return file_url
