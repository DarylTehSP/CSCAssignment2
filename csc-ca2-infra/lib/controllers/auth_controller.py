from http import HTTPStatus
from lib.services.oauth_service import exchange_token
from botocore.utils import _parse_timestamp_with_tzinfo
from lib.services.dynamodb_service import get_user_info, store_session, remove_session
from uuid import uuid4
from lib.webexception import WebException
import jwt


def oauth_redirect(request, response):
    # Take email to authenticate, then when user is authenticated generate session and store session.
    data = request.data
    code_grant = data["code_grant"]

    code = exchange_token(code_grant)

    if code is not None:
        jwt_id_token = code["id_token"]
        id_token = jwt.decode(
            jwt_id_token.encode("utf-8"), options={"verify_signature": False}
        )
        user_id = id_token["email"]
        sessionToken = str(uuid4())
        store_session(sessionToken, user_id)
        user_info = get_user_info(user_id)

        new_user = False
        if user_info is None:
            new_user = True

        response.body = {"new_user": new_user}
        response.set_session(sessionToken)
    else:
        raise WebException(
            status_code=HTTPStatus.BAD_REQUEST, message="Invalid credentials"
        )

    return response


def logout(request, response):
    remove_session(request.session_token)
    response.clear_session()
    return response
