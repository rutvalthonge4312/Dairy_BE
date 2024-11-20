import random 
from django.core.mail import send_mail,send_mass_mail
from blog_be.settings import EMAIL_HOST_USER, DOMAIN
from django.template.loader import render_to_string
from useronbording.models import OTP
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status



def generate_otp():
    otp = random.randint(100000, 999999) 
    return otp

    
def add_otp_entry_to_table(user,otp_code):
    try:
        otp_instance = OTP(
            otp=otp_code,
            user_email=user.email,
            expires_at=timezone.now() + timedelta(minutes=10)  
        )
        otp_instance.save()
        return True
    except Exception as e:
        print(e)
        return False
    
def verify_mail_otp(email,otp):
    try:
        otp_check=OTP.objects.filter(otp=otp,user_email=email)
        if otp_check.exists():
            otp_obj=otp_check.first()
            if(otp==otp_obj.otp):
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False
def sendMail(user):
    try:
            user_mail=user.email
            otp=generate_otp()
            is_done=add_otp_entry_to_table(user,otp)
            print(is_done)
            if is_done:
                subject = "One Time Password"
                email_template_name = "email/access_approved.txt"
                c = { 
                    "product_name":'Zil Bank', 
                    "otp": otp,
                    'site_name': 'Website',
                    'protocol': 'https',
                }
                message = render_to_string(email_template_name, c)
                try:
                    print("HI")
                    send_mail(subject,message,EMAIL_HOST_USER,[user_mail],fail_silently=False,)
                    return True

                except Exception as e:
                    print("Erro")
                    print(e)
                    return False
                    # logging.exception(f"Mail was not sent with exception: {repr(e)}")
            else:
                print("Error While Sending Mail.")
                return False
    except Exception as e:
        print("error")
        print(e)
        return False
    
def sendMailToChnageMail(user,new_mail):
    try:
            user_mail=user.email
            otp=generate_otp()
            is_done=add_otp_entry_to_table(user,otp)
            if is_done:
                subject = "Change Email Request"
                email_template_name = "email/email_change.txt"
                c = { 
                    "product_name":'Zil Bank', 
                    "otp": otp,
                    'email_to_change':new_mail,
                    'site_name': 'Website',
                    'protocol': 'https',
                }
                message = render_to_string(email_template_name, c)
                try:
                    send_mail(subject,message,EMAIL_HOST_USER,[user_mail],fail_silently=False,)
                    return True

                except Exception as e:
                    return False
                    # logging.exception(f"Mail was not sent with exception: {repr(e)}")
            else:
                print("Error While Sending Mail.")
                return False
    except Exception as e:
        print("error")
        print(e)
        return False