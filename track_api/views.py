from rest_framework.views import APIView
from rest_framework.response import Response
from .helpers import Helper
import requests

class Track(APIView):
    ACCEPTED_ACTIONS = ['login', 'logout', 'buy',
                        'review', 'shopping-cart']

    def post(self, request, **kwargs):
        url_ = self.request.META.get('HTTP_REFERER')
        action = kwargs.get('action')
        errors = []
        if action not in self.ACCEPTED_ACTIONS:
            errors.append({'action': f'{action} is not a valid action'})
        body = request.data
        body_check = Helper.track_body_validator(body)
        errors.extend(body_check)
        if errors:
            err_response = {
                          "errors": errors
                        }
            return Response(data=err_response, status=400)
        ip = body.get('ip')
        if ip:
            r, info = Helper.get_ip_info(ip)
        print(url_)

        data = {
            "updated": 'updated',
            "followed": 'followed',
            "followcount": '1'
        }
        return Response(data)
