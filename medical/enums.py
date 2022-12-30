from enum import Enum


class MedicalLoanFormStatus(Enum):
    Submitted = 1
    Paid = 2
    PartiallyRepaid = 3
    Repaid = 4
