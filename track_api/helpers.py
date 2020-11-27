import requests
import json
import urllib3

class Helper:

    @staticmethod
    def track_body_validator(body):
        err = []
        requested_keys = ['ip', 'resolution']
        for k in requested_keys:
            if k not in body:
                err.append({'missing key': f'{k} missing from body'})
        if not err:
            if not isinstance(body.get('ip'), str):
                err.append({'wrong type': 'ip should be string'})
        return err

    @staticmethod
    def get_ip_info(ip:str, fields=None):
        info = {}
        url = f'http://ip-api.com/json/{ip}'
        if fields:
            url = url + "?fields=" + ",".join(fields)
        try:
            r = requests.get(url, timeout=0.00001)
            if r.status_code == 200:
                r_text = json.loads(r.text)
                if r_text.get('status') == 'success':
                    status = r.status_code
                    info.update({k: v for k, v in r_text.items()})
                else:
                    status = 400
                    info.update({k: v for k, v in r_text})
            else:
                status = r.status_code
        except requests.exceptions.Timeout:
            status = 504
            info.update({'reason': 'connection to external api timeout'})
        except Exception as ex:
            status = 500
            info.update({'reason': 'issues with external api'})
        return status, info