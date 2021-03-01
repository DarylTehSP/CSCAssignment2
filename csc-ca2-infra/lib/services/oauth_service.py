import requests
import os
from urllib.parse import unquote


def exchange_token(code_grant):
    decoded_code_grant = unquote(code_grant)
    payload = {
        "code": decoded_code_grant,
        "client_id": os.environ["OAUTH_CLIENT_ID"],
        "client_secret": os.environ["OAUTH_CLIENT_SECRET"],
        "redirect_uri": "https://ab4z15tt79.execute-api.us-east-1.amazonaws.com/dev/Redirect.html",  # use own endpoint
        "grant_type": "authorization_code",
    }

    response = requests.post("https://oauth2.googleapis.com/token", data=payload)

    if response.status_code == requests.codes.ok:
        code = response.json()
        print(code)
        return code
    else:
        return None
