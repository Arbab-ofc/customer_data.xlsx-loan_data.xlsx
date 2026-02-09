from django.db.models import Sum
from apps.loans.models import Loan
from .credit_score import CreditScoreCalculator
from .emi_calculator import EMICalculator


class EligibilityService:
    def __init__(self, customer):
        self.customer = customer

    def check_eligibility(self, loan_amount, interest_rate, tenure):
        """
        Check loan eligibility based on credit score and various factors
        Returns: dict with approval status, corrected_interest_rate, monthly_installment
        """
        credit_score_calculator = CreditScoreCalculator(self.customer)
        credit_score = credit_score_calculator.calculate()

        monthly_installment = EMICalculator.calculate_emi(
            principal=loan_amount,
            annual_rate=interest_rate,
            tenure_months=tenure
        )

        result = {
            'approval': False,
            'corrected_interest_rate': interest_rate,
            'monthly_installment': monthly_installment,
            'message': '',
            'credit_score': credit_score
        }

        if credit_score <= 10:
            result['message'] = 'Credit score too low. Loan rejected.'
            return result

        current_emis_sum = self._calculate_current_emis()
        monthly_salary = float(self.customer.monthly_salary)

        if current_emis_sum + monthly_installment > (0.5 * monthly_salary):
            result['message'] = 'Sum of current EMIs exceeds 50% of monthly salary. Loan rejected.'
            return result

        corrected_rate = self._determine_corrected_interest_rate(credit_score, interest_rate)

        if corrected_rate != interest_rate:
            monthly_installment = EMICalculator.calculate_emi(
                principal=loan_amount,
                annual_rate=corrected_rate,
                tenure_months=tenure
            )
            result['corrected_interest_rate'] = corrected_rate
            result['monthly_installment'] = monthly_installment

        result['approval'] = True
        result['message'] = 'Loan approved'

        return result

    def _calculate_current_emis(self):
        """Calculate sum of all current active EMIs"""
        current_loans = Loan.objects.filter(
            customer=self.customer,
            is_active=True
        )

        total_emis = current_loans.aggregate(
            total=Sum('monthly_repayment')
        )['total'] or 0

        return float(total_emis)

    def _determine_corrected_interest_rate(self, credit_score, requested_rate):
        """
        Determine the corrected interest rate based on credit score
        Rules:
        - credit_score > 50: approve at requested rate
        - 30 < credit_score <= 50: approve only if rate > 12%, else correct to 12%
        - 10 < credit_score <= 30: approve only if rate > 16%, else correct to 16%
        """
        if credit_score > 50:
            return requested_rate
        elif credit_score > 30:
            return max(12.0, requested_rate)
        elif credit_score > 10:
            return max(16.0, requested_rate)
        else:
            return requested_rate
