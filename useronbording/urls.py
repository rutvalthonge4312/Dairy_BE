
from django.urls import path
from .views import login,signup,update_password,update_mPin,email_otp_send,verify_mail,update_email,update_email_verify_otp,profile,getAllUsers
urlpatterns = [
    # path('verify_mobile/', verify_phone,name='verify_phone'),
    path('login/', login,name='login'),
    path('signup/', signup,name='signup'),
    path('update_password/', update_password,name='update_password'),
    path('update_mpin/', update_mPin,name='update_mpin'),
    
    path('send_otp/', email_otp_send,name='email_otp_send'),
    path('verify_mail/', verify_mail,name='verify_mail'),
    path('update_email/', update_email,name='update_email'),
    path('update_email_confirm/', update_email_verify_otp,name='update_email_verify_otp'),
    path('profile/', profile,name='profile'),
    
    path('get-all-users/', getAllUsers,name='get-users'),
    #profile
]
