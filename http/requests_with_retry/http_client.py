from time import sleep
import requests


class HttpClient:
    """Wrapper around requests which provides http session and retries on some kinds of bad responses
    """
    def __init__(self,
                 try_count: int,
                 default_timeout_sec: float = 15.0,
                 retry_wait_interval_sec: float = 3.0,
                 default_headers: dict = {}):
        """try_count: number of tries to perform http request in case of server error responses (500–599)"""
        self.try_count = try_count
        self.retry_wait_interval_sec = retry_wait_interval_sec
        self.default_timeout_sec = default_timeout_sec
        self.session = requests.Session()
        if len(default_headers):
            self.session.headers.update(default_headers)

    def set_default_headers(self, headers: dict):
        """Override default headers
        """
        self.session.headers.update(headers)

    def get(self, url: str, **requests_kwargs) -> requests.Response:
        return self._issue_request("get", url=url, **requests_kwargs)

    def post(self, url: str, **requests_kwargs) -> requests.Response:
        return self._issue_request("post", url=url, **requests_kwargs)

    def patch(self, url: str, **requests_kwargs) -> requests.Response:
        return self._issue_request("put", url=url, **requests_kwargs)

    def _issue_request(self, method: str, url, **requests_kwargs) -> requests.Response:
        if 'timeout' not in requests_kwargs:
            requests_kwargs['timeout'] = self.default_timeout_sec
        # no need to set default headers, it's automatic

        try_num = 0
        while try_num <= self.try_count:
            try_num += 1
            request_str = f"{method} {url}: Try {try_num}/{self.try_count}"
            try:
                r = self.session.request(method=method, url=url, **requests_kwargs)
            except requests.exceptions.ConnectTimeout as e:
                print(f"{request_str}: request has been timed out")
                raise
            except requests.exceptions.ConnectionError as e:
                print(f"{request_str}: request failed with ConnectionError exception. There is a network problem. "
                      f"Can't proceed. Exception body: '{e}'. Response: {e.response}")
                raise
            if r.status_code in range(200, 300):
                print(f"{request_str}: succeed")
                return r
            if r.status_code in range(400, 500):
                print(f"{request_str}: request failed with unrecoverable status {r.status_code} and message '{r.text}'.")
                r.raise_for_status()
            message = f"{request_str}: request failed with status {r.status_code} and message {r.text}"
            if try_num == self.try_count:
                print(f"{message}. Giving up.")
                r.raise_for_status()
                raise Exception("Unexpected behavior of function {__name__}")
            sleep(self.retry_wait_interval_sec)
            print(f"{message}. Retrying...")
        raise Exception("Unexpected behavior of function {__name__}")
