from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from medical import serializers as medical_serializers
from medical import validators as medical_validators
from medical import models as medical_models
from django.core.exceptions import ValidationError

from medical.exceptions import BaseExceptionManager


# Create your views here.


class MedicalLoanView(APIView):
    serializer_class = medical_serializers.MedicalLoanSerializers

    @staticmethod
    def post(request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('email')
        date = request.data.get('date')
        amount = request.data.get('amount')
        loan_period = request.data.get('loan_period')

        try:
            medical_validators.email_validator(email)
        except ValidationError as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            medical_loan_form = medical_models.MedicalLoanForm.objects.create(name=name, email=email,
                                                                              phone_number=phone_number, date=date,
                                                                              amount=amount, loan_period=loan_period)
            serializer = medical_serializers.MedicalLoanSerializers(medical_loan_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseExceptionManager as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
