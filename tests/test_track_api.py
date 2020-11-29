from django.test import SimpleTestCase, Client
from track_api.views import Track
import json


class TestTrackApi(SimpleTestCase):
    client = Client(CONTENT_TYPE="application/json")

    def test_body_validator(self):
        """
        Makes 2 calls: one with valid payload and one with invalid payload.
        Compares responses with expected behaviour for each payload.
        :return:
        """
        valid_payload = {
            "ip": "24.48.0.1",
            "resolution": ""
        }
        bad_payload = {
            "resolution": {}
        }
        good_response = self.client.post('/track/login',
                                         data=valid_payload,
                                         content_type="application/json")
        bad_response = self.client.post('/track/login',
                                        data=bad_payload,
                                        content_type="application/json")
        good_resp = good_response.json()
        bad_resp = bad_response.json()
        self.assertTrue("info" in good_resp)
        self.assertTrue(good_resp["info"]["ip"] == valid_payload["ip"])
        self.assertTrue("errors" in bad_resp)
        self.assertTrue(any("missing key" in i for i in bad_resp["errors"]))

    def test_action_validation(self):
        """
        Makes two calls to 2 different endpoints. One of the actions is an accepted action, the other is not.
        Checks if responses are the appropriate ones.
        :return:
        """
        good_url = '/track/login'
        bad_url = '/track/blah'
        valid_payload = {
            "ip": "24.48.0.1",
            "resolution": ""
        }

        good_response = self.client.post(good_url,
                                         data=valid_payload,
                                         content_type="application/json")
        bad_response = self.client.post(bad_url,
                                        data=valid_payload,
                                        content_type="application/json")
        good_resp = good_response.json()
        bad_resp = bad_response.json()
        self.assertTrue("action" in good_resp and good_resp["action"] == good_url.split("/")[-1])
        # check if bot response status codes are appropriate
        self.assertEqual(good_response.status_code, 200)
        self.assertEqual(bad_response.status_code, 400)

        self.assertTrue(any("action" in i for i in bad_resp["errors"]))
        error_msg = bad_resp["errors"][0].get('action')
        # check if the error response contains the invalid action.
        self.assertTrue(error_msg.startswith(bad_url.split("/")[-1]) and error_msg.endswith("is not a valid action"))

    def test_invalid_ip(self):
        valid_payload_invalid_ip = {
            "ip": "24.48.0.",
            "resolution": ""
        }
        bad_response = self.client.post('/track/login',
                                        data=valid_payload_invalid_ip,
                                        content_type="application/json")
        self.assertEqual(bad_response.status_code, 400)
        bad_resp = bad_response.json()
        error_msg = bad_resp["errors"][0]
        self.assertTrue("status" in error_msg and error_msg["status"] == "fail")
        self.assertTrue("message" in error_msg and error_msg["message"] == "invalid query")
        self.assertTrue("query" in error_msg and error_msg["query"] == valid_payload_invalid_ip["ip"])

    def test_succesfull_call(self):
        """
        Make a valid call and check expected response.
        :return:
        """
        location_keys = ["latitude",
                         "city",
                         "region",
                         "country",
                         "country_iso2",
                         "continent"
                         ]
        valid_url = '/track/login'
        valid_payload = {
            "ip": "24.48.0.1",
            "resolution": ""
        }
        good_response = self.client.post(valid_url,
                                         data=valid_payload,
                                         content_type="application/json")
        good_resp = good_response.json()
        self.assertEqual(good_response.status_code, 200)
        # check if all needed keys and sub-keys are in response
        self.assertTrue("action" in good_resp and good_resp["action"] == valid_url.split("/")[-1])
        self.assertTrue("info" in good_resp and good_resp["info"]["ip"] == valid_payload["ip"])
        self.assertTrue("info" in good_resp and good_resp["info"]["resolution"] == valid_payload["resolution"])
        self.assertTrue("location" in good_resp and all(key in good_resp["location"] for key in location_keys))
        self.assertTrue("action_date" in good_resp)
