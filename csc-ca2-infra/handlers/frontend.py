from http import HTTPStatus
import boto3
import base64
from urllib.parse import unquote_plus
import gzip


def handler(event, context):
    print("Invoked")

    method = event.get("httpMethod", "")
    path = event.get("path", "")

    response = {
        "isBase64Encoded": True,
        "statusCode": HTTPStatus.METHOD_NOT_ALLOWED,
        "body": "",
        "headers": {"content-encoding": "gzip"},
    }
    if method not in ["GET", "HEAD"]:
        return response

    s3client = boto3.client("s3")
    if path == "/":
        path = "Index.html"
    else:
        split_path = path.split("/", 1)
        path = split_path[1]
    try:
        s3objectkey = unquote_plus(path, encoding="utf-8")
        s3object = s3client.get_object(
            Bucket="csc-ca2-static-teh", Key=s3objectkey # Bucket name to be changed
        )
    except Exception:
        s3objectkey = unquote_plus("Index.html", encoding="utf-8")
        s3object = s3client.get_object(
            Bucket="csc-ca2-static-teh  ", Key=s3objectkey # Bucket name to be changed
        )
    print(s3object)
    response = {
        "statusCode": HTTPStatus.OK,
        "body": base64.b64encode(gzip.compress(s3object["Body"].read())).decode(
            "utf-8"
        ),
        "headers": {
            **s3object["ResponseMetadata"]["HTTPHeaders"],
            **{"content-encoding": "gzip"},
        },
        "isBase64Encoded": True,
    }
    print(response)
    return response
