from products.models import Product
from utils_.validation.badwords_validation import EntityBadWordsValidationService


class ProductEntityBadWordsValidateService(EntityBadWordsValidationService):

    def publish(self) -> Product:
        self.obj.public = True
        self.obj.save()
        return self.obj

    def unpublish(self) -> Product:
        self.obj.public = False
        self.obj.save()
        return self.obj
