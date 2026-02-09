from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Loan
from apps.customers.models import Customer
from .serializers import (
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    LoanCreationRequestSerializer,
    LoanCreationResponseSerializer,
    LoanDetailSerializer,
    CustomerLoanSerializer
)
from apps.core.services.eligibility import EligibilityService
from apps.core.services.emi_calculator import EMICalculator


class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer_id = data['customer_id']

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        eligibility_service = EligibilityService(customer)
        eligibility_result = eligibility_service.check_eligibility(
            loan_amount=data['loan_amount'],
            interest_rate=data['interest_rate'],
            tenure=data['tenure']
        )

        response_data = {
            'customer_id': customer_id,
            'approval': eligibility_result['approval'],
            'interest_rate': data['interest_rate'],
            'corrected_interest_rate': eligibility_result['corrected_interest_rate'],
            'tenure': data['tenure'],
            'monthly_installment': eligibility_result['monthly_installment']
        }

        response_serializer = LoanEligibilityResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanCreationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer_id = data['customer_id']

        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        eligibility_service = EligibilityService(customer)
        eligibility_result = eligibility_service.check_eligibility(
            loan_amount=data['loan_amount'],
            interest_rate=data['interest_rate'],
            tenure=data['tenure']
        )

        if not eligibility_result['approval']:
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': eligibility_result['message'],
                'monthly_installment': eligibility_result['monthly_installment']
            }
            response_serializer = LoanCreationResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        final_interest_rate = eligibility_result['corrected_interest_rate']
        monthly_installment = EMICalculator.calculate_emi(
            principal=data['loan_amount'],
            annual_rate=final_interest_rate,
            tenure_months=data['tenure']
        )

        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30 * data['tenure'])

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=Decimal(str(data['loan_amount'])),
            tenure=data['tenure'],
            interest_rate=Decimal(str(final_interest_rate)),
            monthly_repayment=Decimal(str(monthly_installment)),
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        customer.current_debt += Decimal(str(monthly_installment)) * data['tenure']
        customer.save()

        response_data = {
            'loan_id': loan.loan_id,
            'customer_id': customer_id,
            'loan_approved': True,
            'message': 'Loan approved successfully',
            'monthly_installment': float(monthly_installment)
        }

        response_serializer = LoanCreationResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ViewLoanView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        loans = Loan.objects.filter(customer=customer, is_active=True)
        serializer = CustomerLoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
