from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='loans',
        db_column='customer_id'
    )
    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tenure = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(600)]
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    monthly_repayment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['loan_id']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"

    @property
    def repayments_left(self):
        return max(0, self.tenure - self.emis_paid_on_time)
