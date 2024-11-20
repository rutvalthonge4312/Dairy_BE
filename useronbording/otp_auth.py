import random
import requests

from django.conf import settings
def send_otp_request(to):
    number = "+91"+to
    print(number)
    url = f"https://2factor.in/API/V1/{settings.API_KEY}/SMS/{number}/AUTOGEN/mobile_verification"

    try:
        response = requests.get(url)
        print( response.json())
    except requests.RequestException as e:
        return False
    
    data = response.json()

    if data["Status"] == "Success":
        session_id = data["Details"]
        return session_id
    else:
        return None


def verify_otp(session_id, otp_code):
    url = f"https://2factor.in/API/V1/{API_KEY}/SMS/VERIFY/{session_id}/{otp_code}"

    try:
        response = requests.get(url)
    except requests.RequestException as e:
        return False

    data = response.json()

    if data["Status"] == "Success":
        if data["Details"] == "OTP Matched":
            return True
        else:
            return False
    else:
        return False