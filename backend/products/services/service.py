import datetime

from products.models import Product, Sale
from utils.validate_service import BadWordsValidator


class ProductBadWordsValidateService(BadWordsValidator):

    def publish(self) -> Product:
        self.obj.public = True
        self.obj.save()
        return self.obj

    def unpublish(self) -> Product:
        self.obj.public = False
        self.obj.save()
        return self.obj


class SaleValidationService:

    def __init__(self, sale: Sale):
        self.sale = sale

    def validate_sale_expired(self) -> dict[str, bool | str]:
        if self.sale.end_date > datetime.datetime.now():
            return {'success': True}
        return {'success': False, 'message': 'Sale is expired!'}
