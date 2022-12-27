from django.db import models

from medical.exceptions import BaseExceptionManager


# Create your models here.


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MedicalLoanForm(BaseModel):
    name = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(null=True, blank=True, max_length=255)
    date = models.DateTimeField(null=True, blank=True, default=None)
    amount = models.DecimalField(max_digits=32, decimal_places=8, default=0)
    loan_period = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.amount <= 0:
                raise BaseExceptionManager('Amount must be positive.')
            if self.loan_period < 1:
                raise BaseExceptionManager('Loan period cannot be shorter than 1 month.')
            super(MedicalLoanForm, self).save(*args, **kwargs)
        else:
            super(MedicalLoanForm, self).save(*args, **kwargs)
