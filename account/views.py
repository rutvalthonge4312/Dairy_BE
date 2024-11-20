from django.shortcuts import render
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import re
from useronbording.models import User
from .models import Account
from .serializer import CreateAccountSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from useronbording.models import User
from transaction.models import BankTransaction





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addData(request):
    try:
        data=request.data
        serializer_data=CreateAccountSerializer(data=data)
        if(serializer_data.is_valid()):
            bank_name="State Bank of MyWorld"
            phone=request.data['phone']
            balance=request.data['amount']
            account_type=request.data['accountType']
            m_pin=request.data['mPin']
            # m_pin=str(m_pin)
            if not phone:
                return Response({'message': 'Please Enter Mobile Number'}, status=status.HTTP_400_BAD_REQUEST)
            if not m_pin:
                return Response({'message': 'Please give m-pin, for further transcations!'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if(len(m_pin)!=4):
                    return Response({'message': 'm-Pin must be of 4 digits'}, status=status.HTTP_400_BAD_REQUEST)
            user=User.objects.filter(phone_number=phone).exists()
            if(user):
                user = User.objects.filter(phone_number=phone).first()
                if(user.isAccount):
                    return Response({'message': 'Already Have Account!'}, status=status.HTTP_400_BAD_REQUEST)
                user.isAccount=True
                if(Account.objects.exists()):
                    last_accoutNumber=Account.objects.last()
                    new_number=int(last_accoutNumber.account_number)+1
                    newaccountNumber=new_number
                else:
                    newaccountNumber=10001
                account = Account(
                    bank_name=bank_name,
                    account_type=account_type,
                    balance=balance,
                    customer=user,
                    m_pin=m_pin,
                    account_number=newaccountNumber
                )
                user.save()
                account.save()
                return Response({'message': 'Successfully opened Account!'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User with this mobile number does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            error=serializer_data.errors
            return Response({"message":error }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_balance(request):
    try:
        data=request.data
        if data:
            m_pin=data["mPin"]
            if not m_pin:
                return Response({'message': 'Enter m-Pin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if (len(m_pin)!=4):
                    return Response({'message': 'm-Pin should be of 4 digits'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Enter m-Pin'}, status=status.HTTP_400_BAD_REQUEST)
        user=request.user
        user_mobile=user.phone_number
        
        user_account=Account.objects.filter(customer=user)
        if user_account.exists():
            validate_user=user_account.filter(m_pin=m_pin)
            if validate_user:
                balance=user_account.first().balance
                return Response({'message': balance}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Wrong M-pin!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Account Not Found!'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def checkTransferableBalance(balance,account_obj):
    if(int(account_obj.balance)>int(balance)):
        return True
    else:
        return False
def checkPin(m_pin_payload,account_obj):
    if((m_pin_payload)==(account_obj.m_pin)):
        return True
    else:
        return False
    
def add_entry_to_transaction_table(account,transaction_type,amount,transaction_status):
    try:
        transaction_obj=BankTransaction(
            account=account,
            transaction_type=transaction_type,
            amount=amount,
            # date=date,
            transaction_status=transaction_status
        )
        transaction_obj.save()
        return True
    except Exception as e:
        return False
    
@api_view(['POST'])      
@permission_classes([IsAuthenticated])   
def credit_amount_to_another_acoount(request):
    try:
        data=request.data
        user=request.user
        if not data:
            return Response({"message":"Provoid all the required fields" }, status=status.HTTP_400_BAD_REQUEST)
        reciever_mobile_number=data["recieverMobileNumber"]
        m_pin=data["m_pin"]
        if not m_pin:
            return Response({"message":"Provoid the m-Pin" }, status=status.HTTP_400_BAD_REQUEST)
        if not reciever_mobile_number:
            return Response({"message":"Provoid the reciever mobile number" }, status=status.HTTP_400_BAD_REQUEST)
        if reciever_mobile_number:
            if(len(reciever_mobile_number)!=10):
                return Response({"message":"Phone Number Should be of 10 digit only!" }, status=status.HTTP_400_BAD_REQUEST)
        
        #reciever account
        check_reciever_user=User.objects.filter(phone_number=reciever_mobile_number)
        if not (check_reciever_user.exists()):
            return Response({"message":f"Account Not Found For this phone number:{reciever_mobile_number}" }, status=status.HTTP_400_BAD_REQUEST)
        check_reciever_user=check_reciever_user.first()
        check_reciever_user=Account.objects.filter(customer=check_reciever_user)
        check_reciever_user=check_reciever_user.first()
        amount_to_transfer=data["amount"]
        if not amount_to_transfer:
            return Response({"message":"Provoid the amount to transfer" }, status=status.HTTP_400_BAD_REQUEST)
        #user account
        user_account=Account.objects.filter(customer=user)
        if not (user_account.exists()):
            return Response({"message":"Account Not Found For this user." }, status=status.HTTP_400_BAD_REQUEST)
        user_account=user_account.first()
        if(checkTransferableBalance(amount_to_transfer,user_account)):
            try:
                if(checkPin(m_pin,user_account)):
                    user_account.balance=int(user_account.balance)-int(amount_to_transfer)
                    check_reciever_user.balance=int(check_reciever_user.balance)+int(amount_to_transfer)
                    
                    user_account.save()
                    add_entry_to_transaction_table(user_account,'withdrawal',amount_to_transfer,'success')
                    check_reciever_user.save()
                    add_entry_to_transaction_table(check_reciever_user,'deposit',amount_to_transfer,'success')
                    
                    return Response({"message":"Transaction Successfull" }, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Wrong Pin!" }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e)
                add_entry_to_transaction_table(user_account,'withdrawal',amount_to_transfer,'failed')
                add_entry_to_transaction_table(check_reciever_user,'deposit',amount_to_transfer,'failed')
                return Response({"message":"Transaction Failed!" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            add_entry_to_transaction_table(user_account,'withdrawal',amount_to_transfer,'failed')
            return Response({"message":"Insufficeint Bank Balance!" }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message":"Internal Server Error!" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['POST'])      
@permission_classes([IsAuthenticated])     
def reciever_data(request):
    try:
        data=request.data
        phone_number=data["mobile"]
        if not phone_number:
            return Response({"message":"Provoide The Mobile Number!" }, status=status.HTTP_400_BAD_REQUEST)
        if(len(phone_number)!=10):
            return Response({"message":"Mobile Number should be of 10 digit only!" }, status=status.HTTP_400_BAD_REQUEST)
        user_details=User.objects.filter(phone_number=phone_number)
        
        if(user_details.exists()):
            user_details=user_details.first()
            if(user_details==(request.user)):
                return Response({"message":"You Entered your number , you can not transfer amount to yourself" }, status=status.HTTP_400_BAD_REQUEST)
            user_account_details=Account.objects.filter(customer=user_details)
            if(user_account_details.exists()):
                user_account_details=user_account_details.first()
                user_data={
                    "name":f'{user_details.first_name} {user_details.last_name}',
                    "mobile":user_details.phone_number,
                    "bankName":user_account_details.bank_name
                }
                return Response({"message":"User Account Found!" ,"data":user_data }, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Account Not Found!" }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"User Not Found!" }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({"message":"Internal Server Error!" }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)