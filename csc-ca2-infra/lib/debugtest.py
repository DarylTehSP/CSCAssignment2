def debug_test(request,response):
    response.body = {
        "message": "Working",
        "event": request.event
    }
    return response