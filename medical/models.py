from decimal import Decimal

from django.db import models, transaction

from medical.exceptions import BaseExceptionManager
from medical.enums import MedicalLoanFormStatus, LoanRepayEventStatus
from medical.safaricom_api import SafariCom
from medical.ipay_api import IPay


# Create your models here.


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Choices:
    medical_loan_form_status = (
        (item.value, item.name) for item in MedicalLoanFormStatus
    )

    loan_repay_event_status = (
        (item.value, item.name) for item in LoanRepayEventStatus
    )


class MedicalLoanForm(BaseModel):
    name = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(null=True, blank=True, max_length=255)
    date = models.DateTimeField(null=True, blank=True, default=None)
    total_amount = models.DecimalField(max_digits=32, decimal_places=8, default=0)
    remaining_amount = models.DecimalField(max_digits=32, decimal_places=8, default=0)
    loan_period = models.IntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=Choices.medical_loan_form_status,
                                              default=MedicalLoanFormStatus.Paid.value)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.total_amount <= 0:
                raise BaseExceptionManager('Amount must be positive.')
            if self.loan_period < 1:
                raise BaseExceptionManager('Loan period cannot be shorter than 1 month.')
            self.remaining_amount = self.total_amount
            super(MedicalLoanForm, self).save(*args, **kwargs)
        else:
            super(MedicalLoanForm, self).save(*args, **kwargs)

    def repay_loan(self, months_count):
        safari_com = SafariCom(auth=True)
        amount = self.calculate_amount(months_count)
        loan_repay_event = LoanRepayEvent.objects.create(medical_loan_form=self, amount=amount)
        with transaction.atomic():
            medical_loan_form: MedicalLoanForm = MedicalLoanForm.objects.filter(id=self.id).select_for_update().get()
            if medical_loan_form.status not in [MedicalLoanFormStatus.Paid.value,
                                                MedicalLoanFormStatus.PartiallyRepaid.value]:
                raise BaseExceptionManager('status is not in Paid or PartiallyRepaid')

            medical_loan_form.remaining_amount = medical_loan_form.remaining_amount - amount
            if medical_loan_form.remaining_amount == Decimal("0"):
                medical_loan_form.status = MedicalLoanFormStatus.Repaid.value
            elif medical_loan_form.remaining_amount > 0:
                medical_loan_form.status = MedicalLoanFormStatus.PartiallyRepaid.value
            else:
                raise Exception('Error! self.remaining_amount is negative')
            data = safari_com.m_pesa_payment(amount=amount, phone_number=medical_loan_form.phone_number,
                                             account_reference=loan_repay_event.unique_id)
            loan_repay_event.checkout_request_id = data.get('CheckoutRequestID')
            loan_repay_event.status = LoanRepayEventStatus.Paid.value
            loan_repay_event.save(update_fields=['checkout_request_id', 'status', 'updated'])
            medical_loan_form.save(update_fields=['status', 'remaining_amount', 'updated'])

    def calculate_amount(self, months_count):
        amount_to_repay = Decimal(str(months_count / self.loan_period)) * self.total_amount
        amount = min(amount_to_repay, self.remaining_amount)
        if amount == Decimal("0"):
            raise BaseExceptionManager("amount cant be zero")
        return amount

    def request_payment_with_ipay(self, months_count):
        amount = self.calculate_amount(months_count)
        loan_repay_event = LoanRepayEvent.objects.create(medical_loan_form=self, amount=amount)
        i_pay = IPay()
        data = i_pay.request_payment(amount=amount, phone_number=self.phone_number,
                                     account_reference=loan_repay_event.unique_id, email=self.email)
        loan_repay_event.checkout_request_id = data.get('oid')
        loan_repay_event.save(update_fields=['checkout_request_id', 'updated'])
        return data


class LoanRepayEvent(BaseModel):
    medical_loan_form = models.ForeignKey('MedicalLoanForm', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=32, decimal_places=8, default=0)
    unique_id = models.CharField(null=True, blank=True, max_length=255)
    checkout_request_id = models.CharField(null=True, blank=True, max_length=255)
    status = models.PositiveSmallIntegerField(choices=Choices.loan_repay_event_status,
                                              default=LoanRepayEventStatus.Waiting.value)

    def save(self, *args, **kwargs):
        if not self.pk:
            super(LoanRepayEvent, self).save(*args, **kwargs)
            self.unique_id = f'loan_number_{self.id}'
            self.save()
        else:
            super(LoanRepayEvent, self).save(*args, **kwargs)

    def verify_ipay_payment(self, order_id, ivm, qwh, afd, poi, uyt, ifd):
        with transaction.atomic():
            medical_loan_form: MedicalLoanForm = MedicalLoanForm.objects.filter(
                id=self.medical_loan_form.id).select_for_update().get()
            if medical_loan_form.status not in [MedicalLoanFormStatus.Paid.value,
                                                MedicalLoanFormStatus.PartiallyRepaid.value]:
                raise BaseExceptionManager('status is not in Paid or PartiallyRepaid')

            medical_loan_form.remaining_amount = medical_loan_form.remaining_amount - self.amount
            if medical_loan_form.remaining_amount == Decimal("0"):
                medical_loan_form.status = MedicalLoanFormStatus.Repaid.value
            elif medical_loan_form.remaining_amount > 0:
                medical_loan_form.status = MedicalLoanFormStatus.PartiallyRepaid.value
            else:
                raise Exception('Error! self.remaining_amount is negative')
            i_pay = IPay()
            loan_repay_event: LoanRepayEvent = LoanRepayEvent.objects.filter(id=self.id).select_for_update().get()
            if loan_repay_event.status != LoanRepayEventStatus.Waiting.value:
                raise BaseExceptionManager('status is not Waiting')
            loan_repay_event.status = LoanRepayEventStatus.Paid.value
            loan_repay_event.save(update_fields=['status', 'updated'])
            medical_loan_form.save(update_fields=['status', 'remaining_amount', 'updated'])
            i_pay.verify_payment(order_id=order_id, ivm=ivm, qwh=qwh, afd=afd, poi=poi, uyt=uyt, ifd=ifd)
