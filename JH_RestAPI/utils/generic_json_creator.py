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
    if error_code == 0:
        return ''
    if error_code == 1:
        return 'Invalid credentials'
    elif error_code == 2:
        return 'User profile not found.'   
    elif error_code == 3:
        return 'Error occured while updating the google token.'   
    elif error_code == 4:
        return 'Google token has expired. Please refresh Google token.' 
    elif error_code == 5:
        return 'Couldnt logout user...'
    elif error_code == 6:
        return 'Could not login... Please check your credentials...'
    elif error_code == 7:
        return 'Passwords do not match'
    elif error_code == 8:
        return 'That username is taken'
    elif error_code == 9:
        return 'That email is being used'
    elif error_code == 10:
        return 'Invalid parameters...'   
    elif error_code == 11:
        return 'Record not found...'      
    elif error_code == 101:
        return 'Poll could not be found...'   
    elif error_code == 102:
        return 'Missing item_id parameter...'   
    elif error_code == 103:
        return 'Poll answer could not be found...'   
    elif error_code == 104:
        return 'Blog could not be found...'       
    return 'Unknown error'    