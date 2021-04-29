from fractions import Fraction


def amount_to_features(amount, coeficient, reverse=True):
    if reverse:
        return Fraction(amount) / Fraction(coeficient)
    else:
        return Fraction(amount) * Fraction(coeficient)

def amount_from_features(amount_features, coeficient, reverse=True):
    if reverse:
        return Fraction(amount_features) * Fraction(coeficient)
    else:
        return Fraction(amount_features) / Fraction(coeficient)

def amount_allowed(amount, min_step_amount, reverse=True):
    if reverse:
        return Fraction(amount) - Fraction(min_step_amount)
    else:
        return Fraction(amount) + Fraction(min_step_amount)

def amount_allowed_percentage(amount, min_step_percentage, reverse=True):
    if reverse:
        return Fraction(amount) - Fraction(amount) * Fraction(min_step_percentage)
    else:
        return Fraction(amount) + Fraction(amount) * Fraction(min_step_percentage)
