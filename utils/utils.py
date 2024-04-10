from flask import jsonify

STATUS_CODES = {
    200:
    'OK - The request has succeeded.',
    201:
    'Created - The request has been fulfilled and has resulted in one or more new resources being created.',
    204:
    'No Content - The server has successfully fulfilled the request and there is no additional content to send '
    'in the response.',
    400:
    'Bad Request - The server could not understand the request due to invalid syntax.',
    401:
    'Unauthorized - The request requires user authentication.',
    403:
    'Forbidden - The server understood the request but refuses to authorize it.',
    404:
    'Not Found - The server can not find the requested resource.',
    405:
    'Method Not Allowed - The method specified in the request is not allowed for the resource identified by the '
    'request URI.',
    408:
    'Request Timeout - The server did not receive a complete request message within the time that it was '
    'prepared to wait.',
    500:
    'Internal Server Error - The server encountered an unexpected condition that prevented it from fulfilling '
    'the request.',
    502:
    'Bad Gateway - The server, while acting as a gateway or proxy, received an invalid response from an inbound '
    'server it accessed in attempting to fulfill the request.',
    503:
    'Service Unavailable - The server is currently unable to handle the request due to a temporary overload or '
    'scheduled maintenance.',
    504:
    'Gateway Timeout - The server, while acting as a gateway or proxy, did not receive a timely response from an '
    'upstream server it accessed in attempting to complete the request.',
}


def check_params_is_none(params, mode='and'):
    """
    校验字典、对象、单值等键值是否为空
    :param params:str | dict | object
    :param mode: and | or
    :return: True | False
    """
    assert mode in ['and', 'or'], "Mode must be either 'and' or 'or'"

    if isinstance(params, dict):
        values = params.values()
    elif not hasattr(params, '__iter__') or isinstance(
            params, str):    # Check if params is a single value
        values = [params]
    else:    # Assume params is an object
        values = [
            getattr(params, attr) for attr in dir(params)
            if not attr.startswith('__')
        ]

    if mode == 'and':
        return all(value is not None for value in values)
    else:    # mode == 'or'
        return any(value is not None for value in values)



def make_response(code, data=None, message=None):
    """
    Constructs a response object for an API request.

    Parameters:
       code (int): The status code of the response.
       data (Optional[Any]): The data to include in the response. Defaults to None.
       message (Optional[str]): The message to include in the response. Defaults to None.

    Returns:
       Tuple[Dict[str, Any], int]: A tuple containing the response object as a dictionary and the status code.
    """
    # 如果没有提供消息，则使用预定义的描述
    if message is None:
        message = STATUS_CODES.get(code, '')
    return jsonify({'data': data, 'message': message}), code
