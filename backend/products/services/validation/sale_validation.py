from django.utils import timezone
from products.models import Sale


class SaleValidationService:

    def __init__(self, sale: Sale):
        self.sale = sale

    def validate_sale_expired(self) -> dict[str, bool | str]:
        if self.sale.end_date > timezone.now():
            return {'success': True}
        return {'success': False, 'message': 'Sale is expired!'}
