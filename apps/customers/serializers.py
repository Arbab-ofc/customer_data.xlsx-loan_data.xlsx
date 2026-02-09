from rest_framework import serializers
from .models import Customer


class CustomerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18)
    monthly_income = serializers.IntegerField(min_value=0)
    phone_number = serializers.IntegerField()

    def validate_phone_number(self, value):
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists")
        if value < 1000000000 or value > 9999999999:
            raise serializers.ValidationError("Invalid phone number")
        return value

    def create(self, validated_data):
        monthly_income = validated_data.pop('monthly_income')
        customer = Customer.objects.create(
            monthly_salary=monthly_income,
            **validated_data
        )
        return customer


class CustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    monthly_income = serializers.DecimalField(
        source='monthly_salary',
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'name',
            'age',
            'monthly_income',
            'approved_limit',
            'phone_number'
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer_id')

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']
