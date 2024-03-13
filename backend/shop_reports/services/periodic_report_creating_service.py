import logging
from datetime import timedelta

from django.db.models import QuerySet, Sum
from django.utils import timezone
from order.models import Order
from shop.models import Shop
from shop_reports.schema import (
    ProductPeriodicReport,
    ShopPeriodicReport,
    ShopPeriodicSalesReportHeader,
)


class ReportCreator:

    def __init__(self, shop: Shop, period: int = 7):
        self.shop: Shop = shop
        self.period = period

        self._report: ShopPeriodicReport = ShopPeriodicReport(data=[])

        self._period_sales: QuerySet
        self._previous_period_sales: QuerySet

    # TODO: SEGREGATE TO PRODUCT REPORT CREATOR
    def _get_shop_header_data(self) -> ShopPeriodicSalesReportHeader:
        header = ShopPeriodicSalesReportHeader()
        header.shop_sales_count = self._period_sales.count()
        header.profit = self._period_sales.aggregate(Sum('amount'))['amount__sum']
        try:
            previous_period_profit = self._previous_period_sales.aggregate(Sum('amount'))['amount__sum']
            header.profit_gain = ((header.profit - previous_period_profit) / previous_period_profit) * 100
        except Exception as e:
            logging.warning(f'Could not calculate profit in header due to {e}')
            header.profit_gain = 0
        return header

    def _get_product_period_data(self, product: dict) -> ProductPeriodicReport:
        product_report = ProductPeriodicReport()
        product_report.product = product
        product_sales = self._period_sales.filter(**product)
        product_report.sales_count = product_sales.count()
        product_report.sales_quantity = self._period_sales.aggregate(Sum('count'))['count__sum']
        product_report.profit = product_sales.aggregate(Sum('amount'))['amount__sum']

        previous_period_product_sales = self._previous_period_sales.filter(**product)
        previous_period_sales_count = previous_period_product_sales.count()
        previous_period_sales_quantity = previous_period_product_sales.aggregate(Sum('count'))['count__sum']
        previous_period_sales_profit = previous_period_product_sales.aggregate(Sum('amount'))['amount__sum']

        try:
            product_report.profit_gain = (
                (product_report.profit - previous_period_sales_profit) / previous_period_sales_profit) * 100
        except Exception as e:
            logging.warning(f'Could not calculate profit in product {product} due to {e}')
            product_report.profit_gain = 0
        try:
            product_report.sales_count_gain = (
                (product_report.sales_count - previous_period_sales_count) / previous_period_sales_count) * 100
        except Exception as e:
            logging.warning(f'Could not calculate profit in sales_count in {product} due to {e}')
            product_report.sales_count_gain = 0
        try:
            product_report.sales_quantity_gain = (
                (product_report.sales_quantity - previous_period_sales_quantity) / previous_period_sales_quantity) * 100
        except Exception as e:
            logging.warning(f'Could not calculate sales quantity {product} due to {e}')
            product_report.sales_quantity_gain = 0
        return product_report

    def _get_shop_period_sales(self):
        shop_period_sales = Order.objects.filter(
            product__shop=self.shop,
            payment_status=True,
            created_at__gt=timezone.now() - timedelta(days=self.period)
        ).select_related('product')
        return shop_period_sales

    def _get_previous_period_sales(self):
        previous_period_sales = Order.objects.filter(
            product__shop=self.shop,
            payment_status=True,
            created_at__gt=timezone.now() - timedelta(days=self.period * 2),
            created_at__lt=timezone.now() - timedelta(days=self.period)
        )
        return previous_period_sales

    def create_weekly_report(self):
        self._period_sales = self._get_shop_period_sales()
        self._previous_period_sales = self._get_previous_period_sales()

        self._report.header = self._get_shop_header_data()

        for product in self._period_sales.values('product').distinct():
            self._report.data.append(self._get_product_period_data(product))

    def get_report(self) -> ShopPeriodicReport:
        return self._report
