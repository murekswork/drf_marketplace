import json
import datetime
import logging


def dict_to_dataclass(dict_: dict, dataclass_: type):
    """Function to convert dict to dataclass by same fields"""
    same_fields = {
        field: dict_[field] for field in dict_ if field in dataclass_.__annotations__
    }
    if "started_at" in same_fields:
        same_fields["started_at"] = datetime.datetime.fromisoformat(
            same_fields["started_at"]
        )
    return dataclass_(**same_fields)


def consume_django_model_to_dataclass(serialized_model: str, dataclass_: type):
    """Function takes serialized django model and dataclass type and converts it to dataclass object"""
    logging.warning(f"GOT DJANGO MODEL TO DATACLASS OBJECT {serialized_model}")
    deserialized_msg = json.loads(serialized_model)[0]
    model_dict = deserialized_msg["fields"]
    model_dict["id"] = deserialized_msg.pop("pk")
    result = dict_to_dataclass(model_dict, dataclass_)
    logging.warning(f"RESULT IS {result}")
    return result
