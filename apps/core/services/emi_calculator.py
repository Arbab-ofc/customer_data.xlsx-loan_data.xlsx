class EMICalculator:
    @staticmethod
    def calculate_emi(principal, annual_rate, tenure_months):
        """
        Calculate EMI using compound interest formula
        EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        where:
        P = Principal loan amount
        r = Monthly interest rate (annual rate / 12 / 100)
        n = Tenure in months
        """
        if annual_rate == 0:
            return principal / tenure_months

        monthly_rate = annual_rate / (12 * 100)

        emi = (
            principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
        ) / (((1 + monthly_rate) ** tenure_months) - 1)

        return round(emi, 2)
