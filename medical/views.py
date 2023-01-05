from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from medical import serializers as medical_serializers
from medical import validators as medical_validators
from medical import models as medical_models
from django.core.exceptions import ValidationError

from medical.exceptions import BaseExceptionManager
from medical.ipay_api import IPay


# Create your views here.


class MedicalLoanView(APIView):
    serializer_class = medical_serializers.MedicalLoanSerializers

    @staticmethod
    def post(request):
        name = request.data.get('name')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        date = request.data.get('date')
        amount = request.data.get('amount')
        loan_period = request.data.get('loan_period')

        try:
            medical_validators.email_validator(email)
            medical_validators.phone_number_validator(phone_number)
        except ValidationError as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            medical_loan_form = medical_models.MedicalLoanForm.objects.create(name=name, email=email,
                                                                              phone_number=phone_number, date=date,
                                                                              total_amount=amount, loan_period=loan_period)
            serializer = medical_serializers.MedicalLoanSerializers(medical_loan_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseExceptionManager as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RepayLoanView(APIView):
    @staticmethod
    def post(request):
        medical_loan_id = request.data.get('medical_loan_id')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        months_to_repay = int(request.data.get('months_to_repay'))

        try:
            medical_loan_form = medical_models.MedicalLoanForm.objects.get(id=int(medical_loan_id), email=email,
                                                                           phone_number=phone_number)
            medical_loan_form.repay_loan(months_count=months_to_repay)
            medical_loan_form.refresh_from_db()
            serializer = medical_serializers.MedicalLoanSerializers(medical_loan_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except medical_models.MedicalLoanForm.DoesNotExist as ve:
            return Response({'error': 'This medical loan form does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except BaseExceptionManager as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MobileRepayLoanView(APIView):
    @staticmethod
    def post(request):
        medical_loan_id = request.data.get('medical_loan_id')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        months_to_repay = int(request.data.get('months_to_repay'))

        try:
            medical_loan_form = medical_models.MedicalLoanForm.objects.get(id=int(medical_loan_id), email=email,
                                                                           phone_number=phone_number)
            data = medical_loan_form.request_payment_with_ipay(months_count=months_to_repay)

            return Response(data, status=status.HTTP_201_CREATED)
        except medical_models.MedicalLoanForm.DoesNotExist as ve:
            return Response({'error': 'This medical loan form does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except BaseExceptionManager as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def get(request):
        order_id = request.GET.get('id')
        status = request.GET.get('status')
        ivm = request.GET.get('ivm')
        qwh = request.GET.get('qwh')
        afd = request.GET.get('afd')
        poi = request.GET.get('poi')
        uyt = request.GET.get('uyt')
        ifd = request.GET.get('ifd')

        try:
            loan_repay_event = medical_models.LoanRepayEvent.objects.get(checkout_request_id=order_id)
        except medical_models.LoanRepayEvent.DoesNotExist:
            return Response({'error': 'This payment does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if status != "aei7p7yrx4ae34":
            return Response({"error": "payment failed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            loan_repay_event.verify_ipay_payment(order_id=order_id, ivm=ivm, qwh=qwh, afd=afd, poi=poi, uyt=uyt, ifd=ifd)
            loan_repay_event.refresh_from_db()
            serializer = medical_serializers.MedicalLoanSerializers(loan_repay_event.medical_loan_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseExceptionManager as ve:
            return Response({'error': ve.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ve:
            print(ve)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
