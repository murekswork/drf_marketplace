from dataclasses import dataclass


@dataclass
class ShopPeriodicSalesReportHeader:
    shop_sales_count: int = 0
    profit: float = 0
    profit_gain: float = 0


@dataclass
class ProductPeriodicReport:
    product: str = "Product"
    sales_count: int = 0
    sales_count_gain: float = 0
    sales_quantity: int = 0
    sales_quantity_gain: float = 0
    profit: float = 0
    profit_gain: float = 0


@dataclass
class ShopPeriodicReport:
    header: ShopPeriodicSalesReportHeader | None = None
    data: list[ProductPeriodicReport] | None = None
