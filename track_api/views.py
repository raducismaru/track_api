from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json
from datetime import datetime
import pycountry_convert as pc
import pytz
from django.conf import settings


class Track(APIView):

    ACCEPTED_ACTIONS = settings.YAML_CONFIG.track_api.get('accepted_actions')
    BODY_REQUESTED_KEYS = settings.YAML_CONFIG.track_api.get('body_requested_keys')

    def post(self, request, **kwargs):
        """
        Method to handle POST calls to this endpoint.
        """
        action = kwargs.get('action')
        errors = []
        # Check if action is an accepted one.
        if action not in self.ACCEPTED_ACTIONS:
            errors.append({'action': f'{action} is not a valid action'})
        body = request.data
        body_check = self.track_body_validator(body)
        errors.extend(body_check)
        if errors:
            err_response = {
                          "errors": errors
                        }
            return Response(data=err_response, status=400)
        ip = body.get('ip')
        if ip:
            r_status, location_info, timezone = self.get_ip_info(ip)
            if r_status == 200:
                info = {'ip': ip, 'resolution': body.get('resolution')}
                action_date = self.action_date_timezone(timezone)
                return Response(self.build_response(action, info, location_info, action_date), status=200)
            else:

                return Response({"errors": [location_info]}, status=r_status)
        else:
            return Response({"errors": ["ip value was not provided"]}, status=400)

    def track_body_validator(self, body):
        err = []
        for k in self.BODY_REQUESTED_KEYS:
            if k not in body:
                err.append({'missing key': f'{k} missing from body'})
        if not err:
            if not isinstance(body.get('ip'), str):
                err.append({'wrong type': 'ip should be string'})
        return err


    def get_ip_info(self, ip:str, fields=None):
        """
        Calls external api to get location info for provided IP.
        External API also supports fields as query param in case just certain info is needed, not all.
        :param ip: str
        :param fields: list
        :return: int, dict, datetime
        """
        timezone = None
        info = {}
        url = f'http://ip-api.com/json/{ip}'
        if fields:
            url = url + "?fields=" + ",".join(fields)
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                r_text = json.loads(r.text)
                status, info, timezone = self.parse_external_response(r_text)
            else:
                status, info, timezone = r.status_code, {'reason': info}, None
        except requests.exceptions.Timeout:
            status = 504
            info.update({'reason': 'connection to external api timeout'})
        except Exception as ex:
            status = 500
            info.update({'reason': f'issues with external api - {str(ex)}'})
        return status, info, timezone

    def parse_external_response(self, response:dict):
        """
        Parses response from ip-info api.
        External api responds with 200 even if invalid ip is0
         provided so checking 'status' key for success.
        :param response:
        :return: int, dict, str
        """
        response_status = response.get('status')
        if response_status == 'success':
            return 200, {
                "longitude": response.get('lat'),
                "latitude": response.get('lon'),
                "city": response.get('city'),
                "region": response.get('regionName'),
                "country": response.get('country'),
                "country_iso2": response.get('countryCode'),
                "continent": self.country_code_to_continent(response.get('countryCode'))
              }, response.get('timezone')
        else:
            return 400, {k: v for k, v in response.items()}, response.get('timezone')

    def build_response(self, action, info,location, action_date):
        """
        Builds response body.
        :param action: str
        :param info: dict
        :param location: dict
        :param action_date: datetime
        :return: dict
        """
        return {
              "action": action,
              "info": info,
              "location": location,
              "action_date": action_date
            }

    def country_code_to_continent(self, country_iso2_code=None):
        """
        Returns continent name based on country ISO2 code since api used for ip-info did not
        return continent info.
        :param country_iso2_code: str
        :return: str
        """
        if country_iso2_code:
            country_continent_code = pc.country_alpha2_to_continent_code(country_iso2_code)
            return pc.convert_continent_code_to_continent_name(country_continent_code)
        else:
            return None

    def action_date_timezone(self, tz_info):
        """
        Gets current datetime for specified timezone
        :param tz_info: str
        :return: datetime
        """
        try:
            if tz_info:
                return datetime.now(pytz.timezone(tz_info))
        except pytz.exceptions.UnknownTimeZoneError:
            return None
