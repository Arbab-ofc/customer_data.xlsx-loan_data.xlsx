from django.db.models import Sum, Q
from django.utils import timezone
from apps.loans.models import Loan


class CreditScoreCalculator:
    def __init__(self, customer):
        self.customer = customer
        self.score = 0

    def calculate(self):
        """Calculate credit score based on multiple factors (0-100)"""
        self.score = 0

        past_loans = Loan.objects.filter(customer=self.customer)

        if not past_loans.exists():
            return 50

        self._evaluate_payment_history(past_loans)
        self._evaluate_number_of_loans(past_loans)
        self._evaluate_current_year_activity(past_loans)
        self._evaluate_loan_volume(past_loans)
        self._evaluate_current_loans_vs_limit()

        self.score = max(0, min(100, self.score))
        return round(self.score)

    def _evaluate_payment_history(self, past_loans):
        """Factor 1: Past loans paid on time (40 points max)"""
        total_emis = 0
        on_time_emis = 0

        for loan in past_loans:
            total_emis += loan.tenure
            on_time_emis += loan.emis_paid_on_time

        if total_emis > 0:
            on_time_percentage = (on_time_emis / total_emis) * 100
            self.score += (on_time_percentage * 0.4)

    def _evaluate_number_of_loans(self, past_loans):
        """Factor 2: Number of loans taken (20 points max)"""
        loan_count = past_loans.count()

        if loan_count <= 2:
            self.score += 20
        elif loan_count <= 5:
            self.score += 15
        elif loan_count <= 10:
            self.score += 10
        else:
            self.score += 5

    def _evaluate_current_year_activity(self, past_loans):
        """Factor 3: Loan activity in current year (20 points max)"""
        current_year = timezone.now().year
        current_year_loans = past_loans.filter(
            Q(start_date__year=current_year) | Q(end_date__year=current_year)
        )

        if current_year_loans.exists():
            active_loans = current_year_loans.filter(is_active=True)
            if active_loans.count() >= 1 and active_loans.count() <= 3:
                self.score += 20
            elif active_loans.count() > 3:
                self.score += 10
        else:
            self.score += 5

    def _evaluate_loan_volume(self, past_loans):
        """Factor 4: Total loan approved volume (20 points max)"""
        total_volume = past_loans.aggregate(
            total=Sum('loan_amount')
        )['total'] or 0

        if total_volume >= 1000000:
            self.score += 20
        elif total_volume >= 500000:
            self.score += 15
        elif total_volume >= 100000:
            self.score += 10
        else:
            self.score += 5

    def _evaluate_current_loans_vs_limit(self):
        """Factor 5: Current loans vs approved limit - Critical factor"""
        current_loans = Loan.objects.filter(
            customer=self.customer,
            is_active=True
        )

        total_current_loan_amount = current_loans.aggregate(
            total=Sum('loan_amount')
        )['total'] or 0

        if total_current_loan_amount > self.customer.approved_limit:
            self.score = 0
