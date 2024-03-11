import csv
import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Generator

from celery.result import AsyncResult

from celery_app import check_badwords_product
from products.models import Product
from products.serializers import ProductCreateSerializer
from shop.models import ProductUpload, Shop
from utils.readers import DataclassFromTxtFileReader


@dataclass
class ProductUploadLog:
    id: int
    product: str | None = None
    success: str | None = None
    result: str | None = None


@dataclass
class ProductUploadTaskResult:
    id: int
    product: str | None = None
    task_id: str | None = None
    error: str | None = None


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
        self.tasks: list[ProductUploadTaskResult] = []
        self.output_file_name = f'backend/tasks_data/raw/{time.time()}_{shop.slug}.txt'

    def upload(self) -> None:
        # decoded_source = self.source
        """Method reads CSV file and iterates over each row with calling _upload method"""
        decoded_source = self.source.read().decode('utf-8').splitlines()
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
        log = ProductUploadTaskResult(id=row_id, product=row['title'])
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


class UploadLogMaker:

    def __init__(self, task_results_filename: str, upload: ProductUpload):
        self.task_results_filename: str = task_results_filename
        self.upload: ProductUpload = upload

        self._task_results: list[ProductUploadTaskResult] = []

        self.products_count: int = 0
        self.success_count: int = 0
        self.error_count: int = 0

        # self.output_service = CsvOutputLogService

    def _read_tasks_dataclasses_from_file(self) -> None:
        """Method to fill instance task results with dataclasses from file"""
        reader = DataclassFromTxtFileReader(dataclass=ProductUploadTaskResult, file_path=self.task_results_filename)
        self._task_results = reader.read()

    def _check_task_completion(self) -> bool:
        """Method to check for task completion"""
        for result in self._task_results:
            if result.task_id and AsyncResult(result.task_id).ready() is False:
                return False
        return True

    def _make_logs(self) -> list[ProductUploadLog]:
        """Method to generate list of logs based on task results"""
        report_result = []
        for task_result in self._task_results:
            upload_log = ProductUploadLog(id=task_result.id, product=task_result.product)
            if task_result.task_id is None:
                self.error_count += 1
                upload_log.result, upload_log.success = task_result.error, 'error'
            else:
                a_res = AsyncResult(task_result.task_id).result
                if 'was published' in a_res.get('result', ''):
                    self.success_count += 1
                    upload_log.success, upload_log.result = 'success', 'published'
                else:
                    upload_log.success, upload_log.result = 'error', 'not published bad words'
                    self.error_count += 1

            report_result.append(upload_log)
            self.products_count += 1

        return report_result

    def create_report(self) -> list[ProductUploadLog]:
        """Method check task completion, updates upload score in db and returns list of logs of dataclasses"""
        if self._check_task_completion() is True:
            self._read_tasks_dataclasses_from_file()

            logs = self._make_logs()
            self.upload.products_count, self.upload.success_count, self.upload.failed_count = (
                self.products_count, self.success_count, self.error_count)
            self.upload.save()
            return logs
        else:
            raise Exception('Tasks are not completed yet')


class UploadResultsExporter(ABC):

    @abstractmethod
    def __init__(self, input_report_result, output_source):
        self.input_report_result = input_report_result
        self.output_file = output_source

    @abstractmethod
    def export(self):
        raise NotImplementedError


class CsvUploadResultExporter(UploadResultsExporter):

    def __init__(self, input_report_result: list[ProductUploadTaskResult], output_source: str) -> None:
        self.report_result = input_report_result
        self.output_file_path = output_source

    def export(self) -> None:
        """Method to export csv file from list of task result dataclass"""
        with open(f'{self.output_file_path}', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(self.report_result[0].__annotations__.keys())

            for report in self.report_result:
                writer.writerow(report.__dict__.values())


class DataclassUploadResultExporter(UploadResultsExporter):

    def __init__(self, input_report_result: list[ProductUploadTaskResult], output_source: str = '') -> None:
        self.input_report_result = input_report_result
        self.output_source: str = output_source

    def export(self) -> Generator[dict[str, Any], Any, None]:
        """Method to export upload result file as JSON string"""
        return (asdict(log) for log in self.input_report_result)
