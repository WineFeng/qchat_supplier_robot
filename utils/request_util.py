import json


class RequestUtil:

    def __init__(self):
        pass

    @staticmethod
    def get_request_args(request):
        if "GET" == request.method:
            args = request.args
        else:
            if "text/plain" in request.content_type:
                args = json.loads(request.data)
            elif "application/json" in request.content_type:
                args = request.json
            else:
                args = request.form
        return args

