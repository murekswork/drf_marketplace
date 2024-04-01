from dataclasses import dataclass


@dataclass
class ProductUploadResultExportDTO:
    id: int
    product: str | None = None
    success: str | None = None
    result: str | None = None


@dataclass
class ProductUploadTaskStateDTO:
    id: int
    product: str | None = None
    task_id: str | None = None
    error: str | None = None
