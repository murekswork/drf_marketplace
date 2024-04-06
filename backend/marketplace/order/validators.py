from rest_framework.serializers import ValidationError


def positive_integer_validator(value):
    if not isinstance(value, int):
        raise ValidationError(detail="Value must be number!")

    if value < 0:
        raise ValidationError(detail="Value must be positive")

    return value
