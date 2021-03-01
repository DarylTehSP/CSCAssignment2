import logging
import boto3
from time import time
from botocore.exceptions import ClientError
from lib.webexception import WebException


def init_client():
    try:
        return boto3.client("dynamodb", region_name="us-east-1")
    except ClientError as ce:
        logging.exception("DynamoDB Failed")
        raise WebException()


def store_session(session, username):
    db = init_client()
    expiry = int(time()) + 86400
    db.put_item(
        TableName="session-info-dev",
        Item={
            "sessionToken": {"S": session},
            "userID": {"S": username},
            "ttl": {"N": str(expiry)},
        },
    )


def remove_session(session):
    db = init_client()
    db.delete_item(TableName="session-info-dev", Key={"sessionToken": {"S": session}})


def get_session_username(session):
    db = init_client()
    db_result = db.get_item(
        TableName="session-info-dev",
        Key={"sessionToken": {"S": session}},
        ProjectionExpression="userID",
    )
    username = db_result.get("Item", {}).get("userID", {}).get("S", None)
    return username


def get_username_from_customerid(customer_id):
    db = init_client()
    db_result = db.scan(
        ExpressionAttributeValues={":customerID": {"S": customer_id,},},
        FilterExpression="customerID = :customerID",
        ProjectionExpression="userID",
        TableName="user-info-dev",
    )

    username = db_result.get("Items", [{}])[0].get("userID", {}).get("S", None)
    return username


def get_user_info(username):
    db = init_client()
    db_result = db.get_item(TableName="user-info-dev", Key={"userID": {"S": username}},)
    user_id = db_result.get("Item", {}).get("userID", {}).get("S", None)
    customer_id = db_result.get("Item", {}).get("customerID", {}).get("S", None)
    last_payment = db_result.get("Item", {}).get("lastPayment", {}).get("S", None)
    subscription_type = (
        db_result.get("Item", {}).get("subscriptionType", {}).get("S", "Free")
    )

    if user_id is None:
        return None
    else:
        return {
            "userID": user_id,
            "customerID": customer_id,
            "last_payment": last_payment,
            "subscription_type": subscription_type,
        }


def get_customer_id(username):
    db = init_client()
    db_result = db.get_item(TableName="user-info-dev", Key={"userID": {"S": username}},)
    customer_id = db_result.get("Item", {}).get("customerID", {}).get("S", None)

    if customer_id is None:
        return None
    else:
        return customer_id


def create_or_update_user_info(username, customerID, subscription_plan, last_payment):
    db = init_client()
    db.put_item(
        TableName="user-info-dev",
        Item={
            "userID": {"S": username},
            "subscriptionPlan": {"S": subscription_plan},
            "lastPaid": {"S": last_payment},
            "customerID": {"S": customerID},
        },
    )


def delete_item(username):
    db = init_client()
    db.delete_item(TableName="user-info-dev", Key={"userID": {"S": username}})
