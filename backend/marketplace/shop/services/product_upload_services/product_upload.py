import csv
import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict

from celery_app import check_badwords_product
from products.models import Product
from products.serializers import ProductCreateSerializer
from shop.models import Shop
from shop.services.product_upload_services.schemas import ProductUploadTaskStateDTO


class ProductUploader(ABC):

    @abstractmethod
    def __init__(self, source, shop):
        self.source = source
        self.shop = shop

    @abstractmethod
    def upload(self):
        raise NotImplementedError


class ProductCSVUploader(ProductUploader):

    def __init__(self, source: str, shop: Shop):
        super().__init__(source=source, shop=shop)
        self.serializer = ProductCreateSerializer
        self.tasks: list[ProductUploadTaskStateDTO] = []
        self.output_file_name = f'backend/tasks_data/raw/{time.time()}_{shop.slug}.txt'

    def upload(self) -> None:
        # decoded_source = self.source
        """Method reads CSV file and iterates over each row with calling _upload method"""
        decoded_source = self.source
        reader = csv.DictReader(decoded_source)
        for row_id, row in enumerate(reader):
            row['shop_id'] = self.shop.id
            self._upload_row(row, row_id)

    def get_tasks_filename(self) -> str:
        return self.output_file_name

    def save_tasks(self) -> None:
        """Method writes list of dataclasses as json to local file"""
        serialized_tasks = [asdict(task) for task in self.tasks]
        with open(self.output_file_name, 'w+') as output_file:
            output_file.write(json.dumps(serialized_tasks))

    def _upload_row(self, row: dict, row_id: int) -> None:
        """Method to generate product upload results log dataclass"""
        log = ProductUploadTaskStateDTO(id=row_id, product=row['title'])
        serialized_row = self.serializer(data=row)
        try:
            if serialized_row.is_valid(raise_exception=True):
                new_product = Product.objects.create(**row)
                new_product.save()
                check_task = check_badwords_product.delay(new_product.id)
                log.task_id = check_task.id
            else:
                pass
        except Exception as serializer_exc:
            log.error = f'{serializer_exc}'
        self.tasks.append(log)
