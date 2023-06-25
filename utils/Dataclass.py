import dataclasses
import json
import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

alog = logging.getLogger('app')


def jsonify(obj: dataclasses.dataclass, unwanted_keys: List[str] = []) -> str:
    if hasattr(obj, 'json') and unwanted_keys is []:
        alog.debug(f'implemented json attribute {obj.json}')
        return obj.json

    obj_dict = dataclasses.asdict(obj)
    for key in unwanted_keys:
        del obj_dict[key]

    json_str = json.dumps(obj_dict)

    return json_str


@dataclass(slots=True)
class DataClassJson:

    @staticmethod
    @abstractmethod
    def Loads(json_str: str) -> object:
        pass

    @property
    def json(self) -> str:
        self_dict = dataclasses.asdict(self)
        json_str = json.dumps(self_dict)
        return json_str

    # @classmethod doesn't work
    # def loads(cls, json_str: str) -> object:
    #     return cls()
