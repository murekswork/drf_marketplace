from django.db.models import Model


def model_to_dataclass_converter(orm_model: Model, dataclass_):
    same_fields = {
        field.name: getattr(orm_model, field.name)
        for field in orm_model._meta.get_fields()
        if field.name in dataclass_.__annotations__
    }
    return dataclass_(**same_fields)
