from django.db import models
from django.core.validators import MinValueValidator


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18)], null=True, blank=True)
    phone_number = models.BigIntegerField(unique=True)
    monthly_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    approved_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_debt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['customer_id']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    def save(self, *args, **kwargs):
        if not self.approved_limit:
            raw_limit = 36 * float(self.monthly_salary)
            self.approved_limit = round(raw_limit / 100000) * 100000
        super().save(*args, **kwargs)
