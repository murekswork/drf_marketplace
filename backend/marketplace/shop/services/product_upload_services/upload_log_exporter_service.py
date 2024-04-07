import csv
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, Generator

from shop.services.product_upload_services.schemas import ProductUploadResultExportDTO


class UploadResultsExporter(ABC):

    @abstractmethod
    def __init__(self, input_report_result, output_source):
        self.input_report_result = input_report_result
        self.output_file = output_source

    @abstractmethod
    def export(self):
        raise NotImplementedError


class CsvUploadResultExporter(UploadResultsExporter):

    def __init__(
        self,
        input_report_result: list[ProductUploadResultExportDTO],
        output_source: str,
    ) -> None:
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

    def __init__(
        self,
        input_report_result: list[ProductUploadResultExportDTO],
        output_source: str = '',
    ) -> None:
        self.input_report_result = input_report_result
        self.output_source: str = output_source

    def export(self) -> Generator[dict[str, Any], Any, None]:
        """Method to export upload result file as JSON string"""
        return (asdict(log) for log in self.input_report_result)
