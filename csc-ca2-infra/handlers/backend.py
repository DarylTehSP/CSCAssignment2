import json
from http import HTTPStatus
from lib.process import Request, Response
from lib.constants import ALLOWED_ORIGINS, ISE_ERROR_MESSAGE
from lib.webexception import WebException


def handler(event, context):
    print("Invoked")
    request = Request(event)
    print(request.endpoint)
    response = Response(request.origin)

    try:
        request = request.resolve_function().check_csrf().retrieve_user().parse_data()

        function_to_run = request.function

        response = function_to_run(request, response)

    except WebException as we:
        print(we)
        response.status_code = we.status_code
        response.message = we.message
    except Exception as e:
        print(e)
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        response.message = ISE_ERROR_MESSAGE

    headers = {
        "content-type": "application/json",
    }
    if request.origin in ALLOWED_ORIGINS:
        headers["access-control-allow-origin"] = request.origin
        headers["access-control-allow-credentials"] = True

    mv_header = {}
    if response.cookies:
        # final_headers = self.cookie_headers
        final_headers = [
            f"{header} Secure; SameSite=Lax;" for header in response.cookies
        ]

        mv_header["set-cookie"] = final_headers

    response_body = {"data": response.body, "status": response.message}

    return {
        "statusCode": response.status_code.value,
        "body": json.dumps(response_body),
        "headers": headers,
        "multiValueHeaders": mv_header,
    }

    # body = {
    #     "message": "Go Serverless v1.0! Your function executed successfully!",
    #     "input": event
    # }

    # response = {
    #     "statusCode": 200,
    #     "body": json.dumps(body)
    # }

    # return response
