import json
from functools import partial

import requests

from plaid_legacy.errors import PlaidError
from plaid_legacy.version import __version__


ALLOWED_METHODS = {'post'}
DEFAULT_TIMEOUT = 600  # 10 minutes

try:
    from json.decoder import JSONDecodeError
except ImportError:
    # json parsing throws a ValueError in python2
    JSONDecodeError = ValueError


def _requests_http_request(
        url,
        method,
        data,
        headers,
        timeout=DEFAULT_TIMEOUT):
    normalized_method = method.lower()
    headers.update({'User-Agent': 'Plaid Python v{}'.format(__version__)})
    if normalized_method in ALLOWED_METHODS:
        return getattr(requests, normalized_method)(
            url,
            json=data,
            headers=headers,
            timeout=timeout,
        )
    else:
        raise Exception(
            'Invalid request method {}'.format(method)
        )


def _http_request(
        url,
        method=None,
        data=None,
        headers=None,
        timeout=DEFAULT_TIMEOUT,
        is_json=True):
    response = _requests_http_request(
        url,
        method,
        data or {},
        headers or {},
        timeout)

    if is_json or response.headers['Content-Type'] == 'application/json':
        try:
            response_body = json.loads(response.text)
        except JSONDecodeError:
            raise PlaidError.from_response({
                'error_message': response.text,
                'error_type': 'API_ERROR',
                'error_code': 'INTERNAL_SERVER_ERROR',
                'display_message': None,
                'request_id': '',
                'causes': [],
            })
        if response_body.get('error_type'):
            raise PlaidError.from_response(response_body)
        else:
            return response_body
    else:
        return response.content


# helpers to simplify partial function application
post_request = partial(_http_request, method='POST')
