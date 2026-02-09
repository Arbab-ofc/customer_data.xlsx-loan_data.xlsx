from decimal import Decimal


def round_to_nearest_lakh(amount):
    """
    Round amount to nearest lakh (100000)
    """
    return round(float(amount) / 100000) * 100000


def calculate_approved_limit(monthly_salary):
    """
    Calculate approved credit limit
    approved_limit = 36 * monthly_salary, rounded to nearest lakh
    """
    raw_limit = 36 * float(monthly_salary)
    return Decimal(str(round_to_nearest_lakh(raw_limit)))
