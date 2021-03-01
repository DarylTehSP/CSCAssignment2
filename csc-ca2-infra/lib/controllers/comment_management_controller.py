import pymysql
import os
from datetime import datetime
from lib.webexception import WebException
from http import HTTPStatus
from lib.services.dynamodb_service import get_session_username
from lib.services.rds_service import getResult, uploadToSql, insertComment


def get_talent_detail(request, response):
    data = request.data

    try:
        getTalentData = f"Select * from talent where TalentId = {data['talentId']}"
        talentResult = getResult(getTalentData)

        oneResult = talentResult[0]
        talentDict = {
            "urlLink": oneResult["UrlLink"],
            "name": oneResult["Name"],
            "bio": oneResult["Bio"],
        }
        response.body = talentDict
        return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e


def get_comments(request, response):
    data = request.data

    username = get_session_username(data["session"])

    commentList = []

    try:

        createdBy = ""
        createdByCurrentUser = True

        getUserDetails = f"Select s.Subscription from users u, user_subscription s where u.Subscription = s.Id and u.Id = {data['userId']};"

        getCommentOfTalent = f"Select CommentId, c.UserId, Comment, ParentId, c.CreatedAt, c.UpdatedAt, UserName from talent t, comment_management c, users u where c.TalentId = {data['talentId']} and c.TalentId = t.TalentId and u.Id = c.UserId;"

        userData = getResult(getUserDetails)

        userDetail = userData[0]

        allCommentsResult = getResult(getCommentOfTalent)

        for oneComment in allCommentsResult:
            if not oneComment["ParentId"] is None:
                if oneComment["UserId"] == int(data["userId"]):
                    createdBy = "You"
                    createdByCurrentUser = True
                else:
                    createdBy = oneComment["UserName"]
                    createdByCurrentUser = False

                commentDict = {
                    "id": int(oneComment["CommentId"]),
                    "createdByCurrentUser": createdByCurrentUser,
                    "content": oneComment["Comment"],
                    "fullname": createdBy,
                    "parent": oneComment["ParentId"],
                    "created": str(oneComment["CreatedAt"]),
                    "modified": str(oneComment["UpdatedAt"]),
                }

                commentList.append(commentDict)

            else:
                if oneComment["UserId"] == int(data["userId"]):
                    createdBy = "You"
                    createdByCurrentUser = True

                else:
                    createdBy = oneComment["UserName"]
                    createdByCurrentUser = False

                commentDict = {
                    "id": int(oneComment["CommentId"]),
                    "createdByCurrentUser": createdByCurrentUser,
                    "content": oneComment["Comment"],
                    "fullname": createdBy,
                    "parent": None,
                    "created": str(oneComment["CreatedAt"]),
                    "modified": str(oneComment["UpdatedAt"]),
                }

                commentList.append(commentDict)

        response.body = {
            "commentResult": commentList,
            "Subscription": userDetail["Subscription"],
            "Username": username,
        }
        return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e


def create_comment(request, response):
    data = request.data
    now = datetime.now()
    count = 0
    paId = ""

    try:
        insert_comment_query = "Insert into comment_management (UserId, TalentId, Comment, ParentId, CreatedAt, UpdatedAt) Values (%s, %s, %s, %s, %s, %s);"
        getNewCommentId = "Select LAST_INSERT_ID();"
        userId = int(data["userId"])
        comment = data["content"]
        createdAt = now.strftime("%Y-%m-%d %H:%M:%S")
        updatedAt = now.strftime("%Y-%m-%d %H:%M:%S")
        parentId = 0
        if not data["parent"] is None:
            parentId = int(data["parent"])
        else:
            parentId = None
        talentId = int(data["talentId"])
        commentId = insertComment(
            insert_comment_query,
            getNewCommentId,
            (userId, talentId, comment, parentId, createdAt, updatedAt),
        )
        count = 1

        id = [id[0] for id in commentId]

        if count == 1:

            get_new_comment_query = f"Select CommentId, c.UserId, Comment, ParentId, c.CreatedAt, c.UpdatedAt, UrlLink, Name, Bio, FullName, us.Subscription from talent t, comment_management c, users u, user_subscription us where c.TalentId = {data['talentId']} and CommentId = {id[0]} and c.TalentId = t.TalentId and u.Id = c.UserId and u.Subscription = us.Id;"

            comment_result = getResult(get_new_comment_query)

            oneResult = comment_result[0]
            if oneResult["ParentId"] is None:
                paId = None
            else:
                paId = int(oneResult["ParentId"])
            createdBy = ""
            createdByCurrentUser = True
            if int(oneResult["UserId"]) == int(data["userId"]):
                createdBy = "You"
                createdByCurrentUser = True
            else:
                createdBy = oneResult["FullName"]
                createdByCurrentUser = False

            commentDict = {
                "id": int(oneResult["CommentId"]),
                "parent": paId,
                "content": oneResult["Comment"],
                "fullname": createdBy,
                "created": str(oneResult["CreatedAt"]),
                "modified": str(oneResult["UpdatedAt"]),
                "createdByCurrentUser": createdByCurrentUser,
            }
            response.body = commentDict

            return response

    except Exception as e:
        raise WebException(status_code=HTTPStatus.BAD_REQUEST, message=str(e)) from e
