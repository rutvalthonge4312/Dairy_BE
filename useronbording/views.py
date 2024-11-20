from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .otp_auth import send_otp_request,verify_otp
from .models import OTP,User
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from account.models import Account
from .utils import sendMail,sendMailToChnageMail,verify_mail_otp

@api_view(['POST'])
def login(request):
    print(request.data)
    try:
        phone=request.data['phone']
        password=request.data['password']
        if phone is not None and isinstance(phone, str):
                phone = phone.strip()
                if not re.match(r'^\d{10}$', phone):
                    return Response({'message': 'Phone number must be of 10 digits'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'message': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(phone_number=phone).first()
        if user:
            print(user.password)
            user_password = user.check_password(password)
            print(user_password)
            if user_password: 
                user_data=UserSerializer(user).data
                username = user.phone_number
                auth_user = authenticate(request, username=username, password=password)
                if auth_user:
                    user_json_data=user_data
                    token, created = Token.objects.get_or_create(user=user)
                    refresh = TokenObtainPairSerializer.get_token(user)
                    print(token)
                    user_json_data['access_token']=str(refresh.access_token),
                    return Response({'message': 'Login Successfull','data':user_json_data}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Wrong Password",'data':username}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)          

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        user=request.user
        user_data=UserSerializer(user)
        user_data=user_data.data
        return Response({'message': "Profile Fetched Successfully!","data":user_data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllUsers(request):
    try:
        user=request.user
        users=User.objects.all()
        user_data=UserSerializer(users,many=True)
        user_data=user_data.data
        return Response({'message': "Data Fetched Successfully","data":user_data}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def signup(request):
    try:
        data=request.data
        phone_number=data['phone_number']
        first_name=data['first_name']
        re_password=data['re_password']
        password=data['password']
        email=data['email']
        role=data['role']
        last_name=data['last_name']
        username=f'{first_name}_{phone_number}'
        data['username']=username
        if(re_password!=password):
            return Response({"message": "Password and Re-password should be same"}, status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.filter(phone_number=phone_number).first()
        if(user):
            return Response({"message": "Mobile Number Already Taken"}, status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.filter(email=email).first()
        if(user):
            return Response({"message": "Email Already Taken"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=data)
        if(serializer.is_valid()):   
            user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=phone_number
        )
            return Response({"message": "Successfully created account"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)          

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    try:
        data=request.data
        user=request.user
        if data:
            old_pasword=data['oldPassword']
            new_password=data['newPassword']
            phone=user.phone_number
            if(old_pasword==new_password):
                return Response({'message': 'Old and new passwords must be different!'}, status=status.HTTP_400_BAD_REQUEST)
            if(len(old_pasword)<6 or len(new_password)<6):
                return Response({'message': 'Password length must be atleast 6 charactor!'}, status=status.HTTP_400_BAD_REQUEST)
            if(user):
                user=User.objects.get(phone_number=phone)
                user_password = user.check_password(old_pasword)
                if(user_password):
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': "Password Updated!"}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "Old Password did'nt match!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "Please Prvoide all fileds!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_mPin(request):
    try:
        data=request.data
        user=request.user
        if data:
            old_pin=data['oldMpin']
            new_pin=data['newMpin']
            if(old_pin==new_pin):
                return Response({'message': 'Old and new pin must be different!'}, status=status.HTTP_400_BAD_REQUEST)
            if(len(old_pin)!=4 or len(new_pin)!=4):
                return Response({'message': 'M-pin length must be of 4 charactor!'}, status=status.HTTP_400_BAD_REQUEST)
            if(user):
                account=Account.objects.filter(customer=user).first()
                print(account.m_pin)
                if(account):
                    if(account.m_pin == old_pin):
                       account.m_pin=new_pin
                       account.save()
                       return Response({'message': "M-pin Updated!"}, status=status.HTTP_200_OK)
                    else:
                        return Response({'message': "Wrong old M-pin"}, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    return Response({'message': "User Don't have Account!"}, status=status.HTTP_400_BAD_REQUEST) 
            else:
               return Response({'message': 'User Not Found.'}, status=status.HTTP_400_BAD_REQUEST) 
            
        else:
            return Response({'message': "Please Prvoide all fileds!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def email_otp_send(request):
    try:
        
        data=request.data
        if not data:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        phone=data["email"]
        if not phone:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.filter(email=phone)
        if user.exists():
            user_data=user.first()
            isSent=sendMail(user_data)
            if(isSent):
                return Response({'message': "Mail Send Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Failed To Sent Mail."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "User Not Found!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def verify_mail(request):
    try:
        data=request.data
        if not data:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        email=data["email"]
        otp=data["otp"]
        if not email:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        otp_check=OTP.objects.filter(otp=otp,user_email=email)
        if otp_check.exists():
            otp_obj=otp_check.first()
            if(otp==otp_obj.otp):
                user = User.objects.filter(email=email).first()
                if user:
                    user_data=UserSerializer(user).data
                    user_json_data=user_data
                    token, created = Token.objects.get_or_create(user=user)
                    refresh = TokenObtainPairSerializer.get_token(user)
                    user_json_data['access_token']=str(refresh.access_token),
                    otp_obj.delete()
                    return Response({'message': 'Login Successfull','data':user_json_data}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "User Not There!"}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({'message': "Incorrect OTP!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "OTP was not there!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['POST'])  
@permission_classes([IsAuthenticated])
def update_email(request):
    try:
        data=request.data
        user=request.user
        if not data:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        update_email=data["updatedMail"]
        if not update_email:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        check_email_object=User.objects.filter(email=update_email)
        if(check_email_object.exists()):
            return Response({'message': "This Email was Already taken!"}, status=status.HTTP_400_BAD_REQUEST)
        user_object=User.objects.filter(email=(user.email))   
        if user_object.exists():
            user_object=user_object.first()
            isSent=sendMailToChnageMail(user_object,update_email)
            if(isSent):
                return Response({'message': "Mail Send Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Failed To Sent Mail."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "User Not Found!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['POST'])  
@permission_classes([IsAuthenticated])
def update_email_verify_otp(request):
    try:
        data=request.data
        user=request.user
        if not data:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        update_email=data["updatedMail"]
        if not update_email:
            return Response({'message': "Email Required!"}, status=status.HTTP_400_BAD_REQUEST)
        otp=data['otp']
        if not otp:
            return Response({'message': "OTP Required!"}, status=status.HTTP_400_BAD_REQUEST)
        user_object=User.objects.filter(email=(user.email))   
        if user_object.exists():
            user_object=user_object.first()
            if verify_mail_otp(user.email,otp):
                user_object.email=update_email
                user_object.save()
                return Response({'message': "Email Updated!"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "OTP verification failed!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': "User Not Found!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': "Internal server error,"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)