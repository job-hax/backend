import json
from utils.error_codes import ResponseCodes

def create_response(data, success=True, error_code=ResponseCodes.success):
    response = {}
    response['success'] = success
    response['error_code'] = int(error_code.value)
    response['error_message'] = get_error_message(error_code)
    if not success:
        response['data'] = None
    else:    
        response['data'] = data
    return response

def get_error_message(error_code):
    if error_code == ResponseCodes.success:
        return ''
    if error_code == ResponseCodes.invalid_credentials:
        return 'Invalid credentials'
    elif error_code == ResponseCodes.user_profile_not_found:
        return 'User profile not found.'   
    elif error_code == ResponseCodes.couldnt_update_google_token:
        return 'Error occured while updating the google token.'   
    elif error_code == ResponseCodes.google_token_expired:
        return 'Google token has expired. Please refresh Google token.' 
    elif error_code == ResponseCodes.couldnt_logout_user:
        return 'Couldnt logout user...'
    elif error_code == ResponseCodes.couldnt_login:
        return 'Could not login... Please check your credentials...'
    elif error_code == ResponseCodes.passwords_do_not_match:
        return 'Passwords do not match'
    elif error_code == ResponseCodes.username_exists:
        return 'This username is taken'
    elif error_code == ResponseCodes.email_exists:
        return 'This email is being used'
    elif error_code == ResponseCodes.invalid_parameters:
        return 'Invalid parameters...'   
    elif error_code == ResponseCodes.record_not_found:
        return 'Record not found...'      
    elif error_code == ResponseCodes.poll_couldnt_found:
        return 'Poll could not be found...'   
    elif error_code == ResponseCodes.missing_item_id_parameter:
        return 'Missing item_id parameter...'   
    elif error_code == ResponseCodes.poll_answer_couldnt_found:
        return 'Poll answer could not be found...'   
    elif error_code == ResponseCodes.blog_couldnt_found:
        return 'Blog could not be found...'       
    elif error_code == ResponseCodes.invalid_username:
        return 'Invalid username...'      
    return 'Unknown error'    