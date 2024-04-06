import json
from abc import ABC, abstractmethod
from csv import DictReader


class DataclassFromFileReader(ABC):

    def __init__(self, file_path: str, dataclass) -> None:
        self.file_path = file_path
        self.dataclass = dataclass
        self.output_data: list = []

    @abstractmethod
    def read(self) -> list:
        raise NotImplementedError


class DataclassFromTxtFileReader(DataclassFromFileReader):

    def read(self) -> list:
        """Method to fill instance task results with dataclasses from file"""
        with open(self.file_path) as file:
            data = json.load(file)
            for item in data:
                dataclass_instance = self.dataclass(**item)
                self.output_data.append(dataclass_instance)
        return self.output_data


class DataclassFromCsvFileReader(DataclassFromFileReader):

    # TODO: Its very hard operation you should consider what to do with it
    def read(self) -> list:
        """Method to fill instance task results with dataclasses from file"""
        with open(self.file_path) as file:
            file_data = DictReader(file)
            for row in file_data:
                self.output_data.append(
                    self.dataclass(**{key: value for key, value in row.items()})
                )
        return self.output_data
