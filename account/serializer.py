from rest_framework import serializers

class CreateAccountSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    accountType = serializers.CharField(max_length=50)
    mPin = serializers.CharField(max_length=4)

    def validate(self, data):
        if not data.get('phone'):
            raise serializers.ValidationError("Phone number is required.")
        if not data.get('amount'):
            raise serializers.ValidationError("Amount is required.")
        if not data.get('accountType'):
            raise serializers.ValidationError("Account type is required.")
        if not data.get('mPin'):
            raise serializers.ValidationError("MPIN is required.")
        return data
