from products.models import Product
from utils.validate_service import BadWordsValidator


class ProductBadWordsValidateService(BadWordsValidator):

    def publish(self) -> Product:
        self.obj.public = True
        self.obj.save()
        return self.obj
