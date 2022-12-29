from django.contrib import admin

from medical import models as medical_models


# Register your models here.


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ["created", "updated"]


class MedicalLoanFormAdmin(BaseAdmin):
    list_display = [field.name for field in medical_models.MedicalLoanForm._meta.fields]
    search_fields = ['phone_number', 'email']


class LoanRepayEventAdmin(BaseAdmin):
    list_display = [field.name for field in medical_models.LoanRepayEvent._meta.fields]
    search_fields = ['checkout_request_id']


admin.site.register(medical_models.MedicalLoanForm, MedicalLoanFormAdmin)
admin.site.register(medical_models.LoanRepayEvent, LoanRepayEventAdmin)
