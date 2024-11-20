from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from useronbording.models import User
from .models import DailyDairyEntry
from .serializers import DailyDairyEntrySerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addData(request):
    try:
        data=request.data
        user=request.user
        
        user_mobile = data.get("mobile")
        shift = data.get("shift")
        date = data.get("date")
        rate = data.get("rate")
        quantity = data.get("quantity")

        if not user_mobile:
            return Response({"message": "Mobile number is required"}, status=400)
        if not shift:
            return Response({"message": "Shift is required"}, status=400)
        if not date:
            return Response({"message": "Date is required"}, status=400)
        if not rate:
            return Response({"message": "Rate is required"}, status=400)
        if not quantity:
            return Response({"message": "Quantity is required"}, status=400)
        
        if not (shift=="E" or shift=="M"):
            return Response({"message": "Invalude shift"}, status=400)
        
        user=User.objects.filter(phone_number=user_mobile)
        if(user.exists()):
            user=user.first()
        else:
            return Response({"message": "User Not Found"}, status=400)
        
        data={
            'farmer':user,
            'date':date,
            'milk_rate':rate,
            'milk_quantity':quantity,
            'shift':shift,
            
            'created_by':user.phone_number,
            'updated_by':user.phone_number,
        }
        
        data, created = DailyDairyEntry.objects.update_or_create(
                    farmer=user, date=date,shift=shift,
                    defaults=data
                )
        
        if(created):
            return Response({'message': 'Data Added Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Data Updated Successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getData(request,date=None):
    try:
        user=request.user
        # data=request.data
        # date=data['date']
        
        if not date:
            return Response({"message": "Date is required"}, status=400)
        data=DailyDairyEntry.objects.filter(farmer=user,date=date)
        
        serialized_data=DailyDairyEntrySerializer(data,many=True)
        return Response({"message": "Data fetched Successfully","data":serialized_data.data}, status=200)
    except Exception as e:
        print(e)
        return Response({'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)