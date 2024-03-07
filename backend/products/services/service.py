from utils.validate_service import BadWordsValidator

from products.models import Product

class ProductBadWordsValidateService(BadWordsValidator):

    def publish(self) -> Product:
        self.obj.public = True
        self.obj.save()
        return self.obj