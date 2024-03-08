import logging
from abc import ABC, abstractmethod

from celery.result import AsyncResult

from celery_app import check_badwords_product
from products.models import Product
from products.serializers import ProductSerializer, ProductUploadSerializer
from products.services.service import ProductBadWordsValidateService
import csv

from shop.models import ProductUpload


class ProductUploader(ABC):

    @abstractmethod
    def __init__(self, source, shop):
        self.source = source
        self.validate_service = ProductBadWordsValidateService
        self.shop = shop

    @abstractmethod
    def upload(self):
        raise NotImplementedError


class ProductCSVUploader(ProductUploader):

    def __init__(self, source, shop):
        super().__init__(source=source, shop=shop)
        self.serializer: type[ProductUploadSerializer] = ProductUploadSerializer
        self.tasks = []

    def upload(self):
        # decoded_source = self.source
        decoded_source = self.source.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_source)
        for row_id, row in enumerate(reader):
            row['shop_id'] = self.shop.id
            self._upload_row(row, row_id)

    def get_tasks(self):
        return self.tasks

    def _upload_row(self, row: dict, row_id: int):
        log = [row_id, ]
        serialized_row = self.serializer(data=row)
        if serialized_row.is_valid():
            new_product = Product.objects.create(**row)
            new_product.save()
            check_task = check_badwords_product.delay(new_product.id)
            log.append({'task_id': check_task.id})
        else:
            log.append({'error': 'Invalid product data was provided'})
        self.tasks.append(log)


class UploadLogger:

    def __init__(self, task_results, upload):
        self.task_results: list[int, dict] = task_results
        self.upload: ProductUpload = upload

        self.products_count: int = 0
        self.success_count: int = 0
        self.error_count: int = 0

    def check_completed(self):
        for task in self.task_results:
            logging.warning(f'Checking completion of task {task}')
            if task[1].get('task_id', None) is not None:
                logging.warning(f'Task idi is {task[1]}')
                task_res = AsyncResult(task[1].get('task_id'))
                if task_res.ready() is False:
                    return False
        return True

    def make_logs(self):
        upload_results = {}
        for task_id, task_data in self.task_results:
            if task_data.get('task_id') is None:
                upload_results[task_id] = task_data
                self.error_count += 1
            else:
                task_result = AsyncResult(task_data.get('task_id')).result
                if 'was published' in task_result.get('result', ''):
                    self.success_count += 1
                else:
                    self.error_count += 1
                upload_results[task_id] = task_result
            self.products_count += 1
        return upload_results

    def start_work(self):
        if self.check_completed() is True:
            logs = self.make_logs()
            self.upload.products_count, self.upload.success_count, self.upload.failed_count = (
                self.products_count, self.success_count, self.error_count)
            self.upload.save()
            return logs
        else:
            raise Exception('Tasks are not completed yet')
