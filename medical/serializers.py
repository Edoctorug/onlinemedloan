from rest_framework import serializers
from medical import models as medical_models


class MedicalLoanSerializers(serializers.ModelSerializer):

    class Meta:
        model = medical_models.MedicalLoanForm
        fields = '__all__'
