from rest_framework import serializers
from .models import Loan
from apps.customers.serializers import CustomerDetailSerializer


class LoanEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0, max_value=100)
    tenure = serializers.IntegerField(min_value=1, max_value=600)


class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()


class LoanCreationRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0, max_value=100)
    tenure = serializers.IntegerField(min_value=1, max_value=600)


class LoanCreationResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.FloatField()


class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer()
    monthly_installment = serializers.DecimalField(
        source='monthly_repayment',
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        model = Loan
        fields = [
            'loan_id',
            'customer',
            'loan_amount',
            'interest_rate',
            'monthly_installment',
            'tenure'
        ]


class CustomerLoanSerializer(serializers.ModelSerializer):
    monthly_installment = serializers.DecimalField(
        source='monthly_repayment',
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        model = Loan
        fields = [
            'loan_id',
            'loan_amount',
            'interest_rate',
            'monthly_installment',
            'repayments_left'
        ]
