from celery.result import AsyncResult
from shop.models import ProductUpload
from shop.services.product_upload_services.schemas import (
    ProductUploadResultExportDTO,
    ProductUploadTaskStateDTO,
)
from utils_.readers import DataclassFromTxtFileReader


class UploadLogMaker:

    def __init__(self, task_results_filename: str, upload: ProductUpload):
        self.task_results_filename: str = task_results_filename
        self.upload: ProductUpload = upload

        self._task_results: list[ProductUploadTaskStateDTO] = []

        self.products_count: int = 0
        self.success_count: int = 0
        self.error_count: int = 0

        # self.output_service = CsvOutputLogService

    def _read_tasks_dataclasses_from_file(self) -> None:
        """Method to fill instance task results with dataclasses from file"""
        reader = DataclassFromTxtFileReader(
            dataclass=ProductUploadTaskStateDTO, file_path=self.task_results_filename
        )
        self._task_results = reader.read()

    def _check_task_completion(self) -> bool:
        """Method to check for task completion"""
        for result in self._task_results:
            if result.task_id and AsyncResult(result.task_id).ready() is False:
                return False
        return True

    def _make_logs(self) -> list[ProductUploadResultExportDTO]:
        """Method to generate list of logs based on task results"""
        report_result = []
        for task_result in self._task_results:
            upload_log = ProductUploadResultExportDTO(
                id=task_result.id, product=task_result.product
            )
            if task_result.task_id is None:
                self.error_count += 1
                upload_log.result, upload_log.success = task_result.error, 'error'
            else:
                a_res = AsyncResult(task_result.task_id).result
                try:
                    if 'was published' in a_res.get('result', ''):
                        self.success_count += 1
                        upload_log.success, upload_log.result = 'success', 'published'
                    else:
                        upload_log.success, upload_log.result = (
                            'error',
                            'not published bad words',
                        )
                        self.error_count += 1
                except Exception as e:
                    self.error_count += 1
                    upload_log.success, upload_log.result = 'error', f'{e}'

            report_result.append(upload_log)
            self.products_count += 1

        return report_result

    def _fill_upload_data(self):
        self.upload.refresh_from_db()
        (
            self.upload.products_count,
            self.upload.success_count,
            self.upload.failed_count,
        ) = (self.products_count, self.success_count, self.error_count)
        self.upload.save()

    def create_report(self) -> list[ProductUploadResultExportDTO]:
        """Method check task completion, updates upload score in db and returns list of logs of dataclasses"""
        if self._check_task_completion() is True:
            self._read_tasks_dataclasses_from_file()

            logs = self._make_logs()
            errors_counter = 0
            try:
                self._fill_upload_data()
            except Exception as e:
                if errors_counter < 0:
                    self.error_count += 1
                    self._fill_upload_data()
                with open('create_report_method_logs.txt', 'a+') as f:
                    f.write(str(e))

            return logs

        else:
            raise Exception('Tasks are not completed yet')
