from enum import Enum


class MedicalLoanFormStatus(Enum):
    Submitted = 1
    Paid = 2
    PartiallyRepaid = 3
    Repaid = 4


class LoanRepayEventStatus(Enum):
    Waiting = 1
    Paid = 2
