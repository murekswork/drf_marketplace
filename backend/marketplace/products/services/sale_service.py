from products.services.validation.sale_validation import SaleValidationService


class SaleApplicationService:

    def apply_sale(self, sale_size: float, amount: float):
        return amount * ((100 - sale_size) / 100)


class SaleService(SaleValidationService, SaleApplicationService):
    pass
