# boto3 for connection to S3.
import boto3
from botocore.exceptions import ClientError
# logging for logging.
import logging
# uuid for creating Universally Unique IDs.
import uuid
# imghdr for image validation.
import imghdr
# pymysql for mySql connection.
import pymysql
# base64 for base 64 encoding/decoding.
import base64
# io for dealing with file objects with different I/O.
import io
# lib.webexception for raising web exception when an error occurs.
from lib.webexception import WebException
# http for usage of HttpStatusCodes.
from http import HTTPStatus
# clarifai
# from clarifai.rest import ClarifaiApp
# from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
# from clarifai_grpc.grpc.api import service_pb2_grpc
# from clarifai_grpc.grpc.api import service_pb2, resources_pb2
# from clarifai_grpc.grpc.api.status import status_code_pb2
# os for usage of envionment variables.
import os

import json

"""
TODO
Validations before upload
    File must be an image file
    Image must contain human face

POST method (Create)
    Send image file to S3 bucket
    Send link, talent_name and talent_description to mySql.

PUT method (Update)
    Note: image, talent_name and talent_description can be changed.
        Make sure whether changing image will change the URL.
    Basically, strip Upload method and reassemble to fit.

GET method (Read)
    GET all
        Retrieve all values from mySql.
    GET by related search terms
        Search function to sift through via related terms in talent_name and talent_description.

DELETE method (Delete)
    Delete said talent's image in S3 bucket, image link, talent_name and talent_description in mySql.
"""

def init_client():
    try:
        return boto3.client('s3', region_name='us-east-1')
    except ClientError as e:
        logging.error("init_client -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

# def containsHumanFace(base64File):
#     # stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
#     # # Set confidence level after done.
#     # metadata = (('authorization', 'Key 2bf10d6f955744549dbb07cb476eaaf0'),)
#     # request = service_pb2.PostModelOutputsRequest(model_id='f76196b43bbd45c99b4f3cd8e8b40a8a', inputs=[resources_pb2.Input(data=resources_pb2.Data(image=resources_pb2.Image(base64=base64File)))])
#     # response = stub.PostModelOutputs(request, metadata=metadata)

#     # if response.status.code != status_code_pb2.SUCCESS:
#     #     raise WebException(status_code=HTTPStatus.BAD_REQUEST, message="containsHumanFace -- Clarifai API Status Code: " + str(response.status.code))

#     cApp = ClarifaiApp(api_key='2bf10d6f955744549dbb07cb476eaaf0')
#     model = cApp.public_models.get(model_id="7e3ced0ca8e748148f797ff8ac6fc8f3")
#     response = model.predict_by_base64(base64File)

#     confidence = 0
#     for concept in response.outputs[0].data.concepts:
#         if(concept.name == "face"):
#             confidence = concept.value

#     if (confidence >= 0.7):
#         logging.info("containsHumanFace -- Image contains Human Face: Passed")
#         return True
#     else:
#         logging.error("containsHumanFace -- Image contains Human Face: Failed")
#         return False

def uploadToSql(query):
    # Connection to mySql server
    connection = pymysql.connect(host=os.environ["HOST"], user=os.environ["USER"], password=os.environ["PASSWORD"], database=os.environ["DATABASE"])
    logging.info("uploadToSql -- Connection to mySql server successful!")

    try:
        cur = connection.cursor()
        cur.execute(query)
        logging.info("uploadToSql -- Insert query executed.")

    except ClientError as e:
        logging.error(e)
        return False

    finally:
        logging.info("uploadToSql -- Closing mySql connection")
        connection.close()

    return True

def getUUID(URL):
    # Get UUID of target Talent for deletion
    splicedUUID = URL.split("/")[-1]
    logging.info("getUUID -- Target UUID: %s", splicedUUID)
    return splicedUUID

def getAllTalents(request, response):
    connection = pymysql.connect(host=os.environ["RDS_HOST"], user=os.environ["RDS_USER"], password=os.environ["RDS_PASSWORD"], database=os.environ["RDS_DATABASE"])
    logging.info("getAllTalents -- Connection to mySql server successful!")
    try:
        cur = connection.cursor()
        rows = cur.fetchall()
        allTalentsJson = json.dumps(rows)
        response.body = allTalentsJson
        return response

    except ClientError as e:
        logging.error(e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message="uploadImage -- File failed Validations.")
    finally:
        logging.info("uploadToSql -- Closing mySql connection")
        connection.close()

def uploadImage(request, response):
    # Load file
    data = request.data
    print(data)
    file = data["photo"]
    image = base64.b64decode(str(file))

    # Validations
    # if (containsHumanFace(file) == False):
    #     raise WebException(status_code=HTTPStatus.BAD_REQUEST, message="uploadImage -- File failed Validations.")

    # Setting UUID for this file
    objectKey = str(uuid.uuid4())
    logging.info("uploadImage -- New UUID: %s", objectKey)

    # Setting other values
    talent_name = data["talentName"]
    talent_bio = data["talentBio"]
    # UPDATE THIS 2 VARIABLES TO NOT BE HARDCODED
    bucketName = "csc-assignment-2-photo-bucket-aloy"
    bucketRegion = "us-east-1"

    try:
        # Uploading file to S3
        s3 = boto3.resource('s3')
        # obj = s3.Object(bucketName, objectKey)
        # obj.put(Body=file)
        s3.Bucket(bucketName).put_object(key=object, Body=file)

        # Set the s3 URL to current Image
        URL = "https://" + bucketName + ".s3." + bucketRegion + ".amazonaws.com/" + objectKey

        # Upload to mySql table
        insertQuery = "INSERT INTO talent (UrlLink, Name, Bio) VALUES (%s, %s, %s)", (URL, talent_name, talent_bio)
        uploadToSql(insertQuery)

    except Exception as e:
        logging.error("uploadImage -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

    return response

def updateTalent(request, response):
    data = request.data
    file = data["photo"]
    image = base64.b64decode(str(file))
    URL = data["url"]
    targetKey = getUUID(URL)

    # Setting other values
    talent_name = data["talentName"]
    talent_bio = data["talentBio"]
    # UPDATE THIS 2 VARIABLES TO NOT BE HARDCODED
    bucketName = "csc-assignment-photo-bucket-aloy"
    bucketRegion = "us-east-1"

    try:
        s3Response = init_client().upload_fileobj(image, bucketName, targetKey)
        logging.info("updateTalentImage -- S3 Update response: %s", s3Response)

        # Set the s3 URL to current Image
        URL = "https://" + bucketName + ".s3." + bucketRegion + ".amazonaws.com/" + targetKey

        # Update mySql table
        updateQuery = "UPDATE talent SET UrlLink='%s', Name='%s', Bio='%s' WHERE UrlLink LIKE '%s'", (URL, talent_name, talent_bio, targetKey)
        uploadToSql(updateQuery)

    except ClientError as e:
        logging.error("updateTalentImage -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

    return response

def deleteTalent(request, response):
    data = request.data
    URL = data["url"]
    targetKey = getUUID(URL)

    # UPDATE THIS VARIABLE TO NOT BE HARDCODED
    bucketName = "csc-assignment-photo-bucket-aloy"

    try:
        s3Response = init_client().delete_object(bucketName, targetKey)
        logging.info("deleteTalent -- S3 Delete response: %s", s3Response)

        # Delete mySql table
        deleteQuery = "DELETE FROM talents WHERE UrlLink LIKE '%s'", (targetKey)
        uploadToSql(deleteQuery)

    except ClientError as e:
        logging.error("deleteTalent -- %s", e)
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e

    return response
