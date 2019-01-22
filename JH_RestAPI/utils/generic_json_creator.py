import json

def create_response(data, success=True, error_code=0):
    response = {}
    response['success'] = success
    response['error_code'] = error_code
    response['error_message'] = get_error_message(error_code)
    if not success:
        response['data'] = None
    else:    
        response['data'] = data
    return response

def get_error_message(error_code):
    if error_code == 1:
        return 'Invalid credentials'
    return ''    