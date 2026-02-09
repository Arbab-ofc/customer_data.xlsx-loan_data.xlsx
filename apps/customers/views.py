from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomerRegistrationSerializer, CustomerResponseSerializer


class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
