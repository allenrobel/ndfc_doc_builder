"""
Name: ndfc.py
Description:

Methods to login to an NDFC controller and issue
DELETE, GET, POST, PUT requests

Example usage:

### In your shell
export NDFC_IP4=10.1.1.1
export NDFC_PASSWORD=my_password
export NDFC_USERNAME=my_username
export NDFC_LOGGING_CONFIG=/path/to/logging_config.json # optional

### In your script
from ndfc import NDFC

ndfc = NDFC()
# optional (default is 20)
ndfc.request_timeout = 30
# optional (default is False)
ndfc.request_verify = True
ndfc.login()
"""
import logging
from os import environ
import json
import sys

import requests
import urllib3

OUR_VERSION = 108


class NdfcRequestError(Exception):
    """
    Use for any uncaught errors associated with NDFC REST API requests
    """


class NDFC:
    """
    Methods to login to an NDFC controller and send DELETE,
    GET, POST, PUT requests to NDFC's REST endpoints

    Usage:

    # In your shell
    export NDFC_IP4=10.1.1.1
    export NDFC_PASSWORD=my_password
    export NDFC_USERNAME=my_username
    # In your script
    from ndfc_python.log import Log
    from ndfc_python.ndfc import NDFC

    ndfc = NDFC()
    ndfc.login()
    """

    def __init__(self):
        self.class_name = __class__.__name__

        self.log = logging.getLogger(f"dcnm.{self.class_name}")

        self._init_login_properties()
        self.lib_version = OUR_VERSION
        self.headers = {}
        self.response = None
        self.auth_token = None
        self.bearer_token = None
        self.properties_set = set()
        self.properties_set.add("request_verify")
        self.properties_set.add("request_timeout")
        self._valid_request_types = set()
        self._valid_request_types.add("DELETE")
        self._valid_request_types.add("GET")
        self._valid_request_types.add("POST")
        self._valid_request_types.add("PUT")
        self._init_properties()

    def _init_login_properties(self):
        """
        initialize login properties from the environment
        """
        self.ip4 = environ.get("NDFC_IP4", None)
        self.password = environ.get("NDFC_PASSWORD", None)
        self.username = environ.get("NDFC_USERNAME", None)
        if self.ip4 is None:
            msg = "Unable to read NDFC_IP4 from the environment. "
            msg += "Please set it and try again. (e.g. export NDFC_IP4=10.1.1.1)"
            print(msg)
            self.log.error(msg)
            sys.exit(1)
        if self.password is None:
            msg = "Unable to read NDFC_PASSWORD from the environment. "
            msg += "Please set it and try again. (e.g. export NDFC_PASSWORD=mypassword)"
            print(msg)
            self.log.error(msg)
            sys.exit(1)
        if self.username is None:
            msg = "Unable to read NDFC_USERNAME from the environment. "
            msg += "Please set it and try again. (e.g. export NDFC_USERNAME=admin)"
            print(msg)
            self.log.error(msg)
            sys.exit(1)

    def _init_properties(self):
        """
        initialize all properties to None
        set defaults for properties that should have one
        """
        self.properties = {}
        for param in self.properties_set:
            self.properties[param] = None
        self.properties["request_verify"] = False
        self.properties["request_timeout"] = 20
        self.properties["verb"] = None

    def login(self):
        """
        login to an NDFC controller
        """
        for key, value in self.properties.items():
            if value is None:
                msg = f"exiting. Set property {key} before calling login."
                self.log.error(msg)
                sys.exit(1)
        urllib3.disable_warnings()
        payload = {}
        payload["userName"] = self.username
        payload["userPasswd"] = self.password
        payload["domain"] = "DefaultAuth"
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Connection"] = "keep-alive"

        self.response = requests.post(
            self.url_login,
            headers=headers,
            data=json.dumps(payload),
            timeout=self.request_timeout,
            verify=False,
        )
        response = json.loads(self.response.text)
        if "jwttoken" not in response:
            msg = "Exiting. Response missing jwttoken in response. "
            msg += "Check password or username?"
            self.log.error(msg)
            self._log_error(self.url_login, "POST")
            sys.exit(1)
        self.auth_token = response["jwttoken"]
        self.bearer_token = f"Bearer {self.auth_token}"

    def make_headers(self):
        """
        return auth and content-type request headers expected by the NDFC
        """
        self.headers = {}
        self.headers["Authorization"] = self.bearer_token
        self.headers["Content-Type"] = "application/json"
        return self.headers

    def _log_error(self, url, request_type):
        """
        Boilerplate error log to corral this in one place.
        """
        msg = f"{request_type} response from NDFC controller during {url}"
        msg += f" response.status_code: {self.response.status_code}"
        self.log.error(msg)
        try:
            msg = (
                f"response.reason: {self.response.reason}"
                f" response.text: {self.response.text}"
            )
            self.log.error(msg)
        except (AttributeError, ValueError) as exception:
            msg = f"Error while logging response for {url}. "
            msg += f"Exception detail {exception}"
            self.log.error(msg)

    def _make_headers(self, params):
        """
        populate headers for ndfc_action
        """
        if "headers" not in params:
            headers = self.make_headers()
        elif params["headers"] is None:
            headers = {}
        else:
            headers = params["headers"]
        return headers

    def _make_payload(self, params):
        """
        populate payload for ndfc_action
        """
        payload: dict[str, str] = {}
        if "payload" in params:
            payload = params["payload"]
        return payload

    def _make_request_params(self, params):
        """
        populate request_params for ndfc_action
        """
        request_params = {}
        if "params" in params:
            request_params = params["params"]
        return request_params

    def ndfc_action(self, params):
        """
        Send GET, POST, PUT, DELETE requests to NDFC

        params is a dictionary with the following keys
        (mandatory keys denoted with *)

        headers -  dictionary or None, headers to send with the request
                    -   Set to None if an empty dictionary is desired
                    -   Omit if standard headers are desired (see
                        self.make_headers)
                    -   Populate if custom headers are desired
        params  -   dictionary, parameters, if any, to send with GET requests
                    - Omit if no parameters
        payload -   dictionary, the request payload
                    - Omit if no payload
        *request_type - string: one of DELETE, GET, POST, PUT
        *url    -   string: the REST API endpoint
        """
        mandatory_keys = {"url", "request_type"}
        if not mandatory_keys.issubset(params):
            msg = f"exiting. expected keys {mandatory_keys}. got {params}"
            self.log.error(msg)
            sys.exit(1)
        if params["request_type"] not in self._valid_request_types:
            msg = f"exiting. invalid request type {params['request_type']} "
            msg += f"expected one of {self._valid_request_types}"
            self.log.error(msg)
            sys.exit(1)
        request_type = params["request_type"]
        url = params["url"]
        request_params = self._make_request_params(params)
        headers = self._make_headers(params)
        payload = self._make_payload(params)

        # print(f"request_type {request_type}")
        # print(f"url {url}")
        # print(f"request_params {request_params}")
        # print(f"headers {headers}")
        # print(f"payload {json.dumps(payload)}")

        try:
            if request_type == "DELETE":
                self.response = requests.delete(
                    url,
                    timeout=self.request_timeout,
                    verify=self.request_verify,
                    headers=headers,
                )
            if request_type == "GET":
                self.response = requests.get(
                    url,
                    params=request_params,
                    timeout=self.request_timeout,
                    verify=self.request_verify,
                    headers=headers,
                )
            if request_type == "POST":
                self.response = requests.post(
                    url,
                    data=json.dumps(payload),
                    timeout=self.request_timeout,
                    verify=self.request_verify,
                    headers=headers,
                )
            if request_type == "PUT":
                self.response = requests.put(
                    url,
                    data=json.dumps(payload),
                    timeout=self.request_timeout,
                    verify=self.request_verify,
                    headers=headers,
                )
        except requests.exceptions.InvalidSchema as exception:
            msg = f"Exiting. error connecting to {url} "
            msg += f"Exception detail: {exception}"
            self.log.error(msg)
            sys.exit(1)
        except requests.ConnectTimeout as exception:
            msg = f"Exiting. Timed out connecting to {url} "
            msg += f"Exception detail: {exception}"
            self.log.error(msg)
            sys.exit(1)
        except requests.ConnectionError as exception:
            msg = f"Exiting. Unable to connect to {url} "
            msg += f"Exception detail: {exception}"
            self.log.error(msg)
            sys.exit(1)

        if self.response.status_code != 200:
            msg = f"status {self.response.status_code} for {request_type} "
            msg += f"url {url}"
            raise NdfcRequestError(msg)
        msg = f"{request_type} succeeded {url}"
        self.log.debug(msg)
        try:
            response = self.response.json()
        except json.decoder.JSONDecodeError:
            response = self.response
        return response

    def get(self, url, headers=None, parameters=None, verify=False):
        """
        call self.ndfc_action() with a GET request
        """
        params = {}
        params["request_type"] = "GET"
        params["url"] = url
        if headers is not None:
            params["headers"] = headers
        if parameters is not None:
            params["params"] = parameters
        params["verify"] = verify
        return self.ndfc_action(params)

    def post(self, url, headers=None, payload=None):
        """
        call self.ndfc_action() with a POST request
        """
        params = {}
        params["request_type"] = "POST"
        params["url"] = url
        if headers is not None:
            params["headers"] = headers
        if payload is not None:
            params["payload"] = payload
        return self.ndfc_action(params)

    def put(self, url, headers, payload=None):
        """
        call self.ndfc_action() with a PUT request
        """
        params = {}
        params["request_type"] = "PUT"
        params["url"] = url
        params["headers"] = headers
        if payload is not None:
            params["payload"] = payload
        return self.ndfc_action(params)

    def delete(self, url, headers):
        """
        call self.ndfc_action() with a DELETE request
        """
        params = {}
        params["request_type"] = "DELETE"
        params["url"] = url
        params["headers"] = headers
        return self.ndfc_action(params)

    @property
    def logger(self):
        """
        return the current logger instance
        """
        return self.log

    @property
    def url_base(self):
        """
        Return the base URL for the NDFC controller
        """
        return f"https://{self.ip4}"

    @property
    def url_login(self):
        """
        Return the login URL for the NDFC controller
        """
        return f"{self.url_base}/login"

    @property
    def url_api_v1(self):
        """
        Return the V1 API URL for the NDFC controller
        """
        return f"{self.url_base}/appcenter/cisco/ndfc/api/v1"

    @property
    def url_control_fabrics(self):
        """
        Return the fabric control API URL for the NDFC controller
        """
        return f"{self.url_api_v1}/lan-fabric/rest/control/fabrics"

    @property
    def url_top_down_fabrics(self):
        """
        Return the top down fabric URL for the NDFC controller
        """
        return f"{self.url_api_v1}/lan-fabric/rest/top-down/fabrics"

    @property
    def url_control_policies_switches(self):
        """
        Return the fabric control API URL for the NDFC controller
        """
        return f"{self.url_api_v1}/lan-fabric/rest/control/policies/switches"

    @property
    def verb(self):
        """
        getter: return the verb (request method).
        setter: set the verb.
        setter: raise ``ValueError`` if verb is not valid.
        """
        return self.properties["verb"]
    @verb.setter
    def verb(self, value):
        if value not in self._valid_request_types:
            msg = f"Invalid verb {value}.  Expected one of "
            msg += f"{','.join(self._valid_request_types)}"
            raise ValueError(msg)
        self.properties["verb"] = value

    @property
    def request_timeout(self):
        """
        Timeout (in seconds) for requests to the NDFC

        Valid values: integer
        Default value: 20
        """
        return self.properties["request_timeout"]

    @request_timeout.setter
    def request_timeout(self, param):
        if not isinstance(param, int):
            msg = f"exiting. expected integer, got {param}"
            self.log.error(msg)
            sys.exit(1)
        self.properties["request_timeout"] = param

    @property
    def request_verify(self):
        """
        verify (True) or do not verify (False) requests

        Valid values: boolean
        Default value: False
        """
        return self.properties["request_verify"]

    @request_verify.setter
    def request_verify(self, param):
        if not isinstance(param, bool):
            msg = f"exiting. expected boolean, got {param}"
            self.log.error(msg)
            sys.exit(1)
        self.properties["request_verify"] = param

    @property
    def response_text(self):
        """
        Return the response text from the last request
        """
        return self.response.text
    @property
    def response_content(self):
        """
        Return the response content from the last request
        """
        return self.response.content
    @property
    def response_status_code(self):
        """
        Return the response status code from the last request
        """
        return self.response.status_code
    @property
    def response_json(self):
        try:
            return self.response.json()
        except json.decoder.JSONDecodeError:
            msg = f"{self.class_name}.response_json: Error decoding JSON "
            msg += "response, returning undecoded response instead."
            print(msg)
            return self.response
