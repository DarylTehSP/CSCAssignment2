import pymysql
import logging
from lib.webexception import WebException
import os


def init_client():
    try:
        connection = pymysql.connect(
            host=os.environ["RDS_HOST"],
            user=os.environ["RDS_USER"],
            password=os.environ["RDS_PASSWORD"],
            database=os.environ["RDS_DATABASE"],
        )
        logging.info("Connection to mySql server successful!")
        return connection
    except WebException as e:
        logging.exception("RDS MySQL Connection Failed")
        raise WebException()


def insertUserData(username, customerID, subscription_plan, last_payment):
    connection = init_client()
    logging.info("insertUserData -- Connection to mySql server successful!")

    try:
        insert_stmt = "Insert into user_data (UserName, CustomerId, SubscriptionPlan, LastPayment) Values (%s, %s, %s, %s);"
        cur = connection.cursor()
        cur.execute(
            insert_stmt, (username, customerID, subscription_plan, last_payment)
        )
        connection.commit()
        logging.info("insertUserData -- Insert query executed.")

    except WebException as e:
        logging.error(e)
        return False

    finally:
        logging.info("insertUserData -- Closing mySql connection")
        connection.close()

    return True


def getResult(query):
    connection = init_client()
    logging.info("getQuery -- Connection to mySql server successful!")

    try:
        cur = connection.cursor(pymysql.cursors.DictCursor)
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        return result

    except WebException as e:
        logging.error(e)
        return False

    finally:
        logging.info("getQuery -- Closing mySql connection")
        connection.close()


def uploadToSql(query, parameters):
    # Connection to mySql server
    connection = init_client()
    logging.info("uploadToSql -- Connection to mySql server successful!")

    try:
        cur = connection.cursor()
        cur.execute(query, parameters)
        connection.commit()
        logging.info("uploadToSql -- Insert query executed.")

    except WebException as e:
        logging.error(e)
        return False

    finally:
        logging.info("uploadToSql -- Closing mySql connection")
        connection.close()

    return True


def insertComment(insertQuery, retrieveNewCommentId, parameters):
    # Connection to mySql server
    connection = init_client()
    logging.info("insertComment -- Connection to mySql server successful!")

    try:
        cur = connection.cursor()
        cur.execute(insertQuery, parameters)
        connection.commit()
        cur.execute(retrieveNewCommentId)
        result = cur.fetchall()
        logging.info("insertComment -- Insert query executed.")
        return result

    except WebException as e:
        logging.error(e)
        return False

    finally:
        logging.info("insertComment -- Closing mySql connection")
        connection.close()

