from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from users import views

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('activate', views.activate_user),
    path('forgotPassword', views.forgot_password),
    path('validateForgotPassword', views.check_forgot_password),
    path('resetPassword', views.reset_password),
    path('sendActivationCode', views.send_activation_code),
    path('changePassword', views.change_password),
    path('updateProfile', views.update_profile),
    path('updateProfilePhoto', views.update_profile_photo),
    path('employmentStatuses', views.employment_statuses),
    path('employmentAuthorizations', views.employment_authorizations),
    path('authSocialUser', views.auth_social_user),
    path('linkSocialAccount', views.link_social_account),
    path('profile', views.get_profile),
    path('refreshToken', views.refresh_token),
    path('syncUserEmails', views.sync_user_emails),
    path('updateGmailToken', views.update_gmail_token),
    path('feedback', views.feedback),
    path('deleteUser', views.delete_user),
    path('verifyRecaptcha', views.verify_recaptcha),
]
urlpatterns = format_suffix_patterns(urlpatterns)
