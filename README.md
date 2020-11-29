API with one endpoint /track/{str:action}.

built with django and django rest framework
* Returns 200 for success
    * valid response: {
                      "action": "<the action>",
                      "info": {
                        "ip": "the ip in payload",
                        "resolution": <resolution in payload>
                      },
                      "location": {
                        "longitude": 0,
                        "latitude": 0,
                        "city": "string",
                        "region": "string",
                        "country": "string",
                        "country_iso2": "string",
                        "continent": "string"
                      },
                      "action_date": "string"(date and time of ip timezone)
                    }
    * invalid response: {
                          "errors": [
                            {}
                          ]
                        }
                        , status 400 and details about errors

* Has some validations for actions(only actions specified in config.yml are allowed)                        
* install dependencies in requirements.txt
* run with python manage.py runserver
* call with Postman
    * method: POST
    * body: {"ip": "<any valid/invalid ip>", 
             "resolution": {
                      "width": 0,
                      "height": 0
                    }
                }
* run tests with python manage.py test
