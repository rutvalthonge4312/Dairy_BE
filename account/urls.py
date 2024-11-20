
from django.urls import path
from .views import check_balance,credit_amount_to_another_acoount,reciever_data
urlpatterns = [
    # path('open_account/', openAccountNumber,name='open_account'),
    path('check_balance/', check_balance,name='check_balance'),
    path('reciever_data/', reciever_data,name='reciever_data'),
    path('credit_amount_to_another_acoount/', credit_amount_to_another_acoount,name='credit_amount_to_another_acoount'),
]
