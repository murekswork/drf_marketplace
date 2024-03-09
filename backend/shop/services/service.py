import csv
import json
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

from celery.result import AsyncResult
from celery_app import check_badwords_product
from products.models import Product
from products.serializers import ProductCreateSerializer
from products.services.service import ProductBadWordsValidateService
from shop.models import ProductUpload, Shop


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


# ProductUploadLog = namedtuple('ProductUploadLog', ['id', 'success', 'result'])

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


class UploadLogger:

    def __init__(self, task_results_filename: str, upload: ProductUpload):
        self.task_results_filename: str = task_results_filename
        self.task_results: list[ProductUploadTaskResult] = []
        self.upload: ProductUpload = upload

        self.products_count: int = 0
        self.success_count: int = 0
        self.error_count: int = 0

        # self.output_service = CsvOutputLogService

    def read_dataclasses_from_file(self) -> None:
        """Method to fill instance task results with dataclasses from file"""
        with open(self.task_results_filename) as file:
            data = json.load(file)
            for item in data:
                dataclass_instance = ProductUploadTaskResult(**item)
                self.task_results.append(dataclass_instance)

    def check_completed(self) -> bool:
        """Method to check for task completion"""
        for result in self.task_results:
            if result.task_id is not None:
                task_res = AsyncResult(result.task_id)
                if task_res.ready() is False:
                    return False
        return True

    def make_logs(self) -> list[ProductUploadLog]:
        """Method to generate list of logs based on task results"""
        report_result = []
        for result in self.task_results:
            upload_log = ProductUploadLog(id=result.id, product=result.product)
            if result.task_id is None:
                self.error_count += 1
                upload_log.result = result.error
                upload_log.success = 'error'
            else:
                task_result = AsyncResult(result.task_id).result
                if 'was published' in task_result.get('result', ''):
                    self.success_count += 1
                    upload_log.success = 'success'
                    upload_log.result = 'published'
                else:
                    upload_log.success = 'error'
                    upload_log.result = 'not published bad words'
                    self.error_count += 1

            report_result.append(upload_log)
            self.products_count += 1

        return report_result

    def start_work(self) -> list[ProductUploadLog]:
        """Method check task completion, updates upload score in db and returns list of logs of dataclasses"""
        if self.check_completed() is True:
            logs = self.make_logs()

            self.upload.products_count, self.upload.success_count, self.upload.failed_count = (
                self.products_count, self.success_count, self.error_count)
            self.upload.save()
            return logs
        else:
            raise Exception('Tasks are not completed yet')


class CsvOutputLogService:

    def __init__(self, report_result: list[ProductUploadTaskResult], file_path: str) -> None:
        self.report_result = report_result
        self.file_path = file_path

    def export_csv(self) -> None:
        """Method to export csv file from list of task result dataclass"""
        with open(f'{self.file_path}', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(self.report_result[0].__annotations__.keys())

            for report in self.report_result:
                writer.writerow(report.__dict__.values())
