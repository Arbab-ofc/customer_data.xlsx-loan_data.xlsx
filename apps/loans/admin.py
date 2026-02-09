from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'interest_rate',
                    'tenure', 'monthly_repayment', 'is_active', 'start_date', 'end_date']
    search_fields = ['loan_id', 'customer__first_name', 'customer__last_name']
    list_filter = ['is_active', 'start_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
