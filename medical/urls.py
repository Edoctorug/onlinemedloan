from django.urls import path, include
from . import views

urlpatterns = [
   path('loan_form/', views.MedicalLoanView.as_view()),
   path('repay-loan/', views.RepayLoanView.as_view()),
]
