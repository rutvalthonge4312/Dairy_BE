from rest_framework import serializers
import re

from .models import DailyDairyEntry




class DailyDairyEntrySerializer(serializers.ModelSerializer):
    farmer = serializers.CharField(required=True)


    class Meta:
        model = DailyDairyEntry
        fields = '__all__'

