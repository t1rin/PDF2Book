from enum import IntEnum
import json
import os
from typing import Any

from utils import resource_path


class MODE(IntEnum):
    PREVIEW = 0
    VISUALIZATION = 1


class Config:    
    def __init__(self, json_path: str = 'config.json') -> None:
        self._path: str = resource_path(json_path)
        self._data: dict = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self._path):
            with open(self._path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else: return {}
    
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            attr = self._data[name]
            if (name == 'formats') and isinstance(attr, dict):
                return dict([*zip(list(attr.keys()), 
                                  map(tuple, list(attr.values())))])
            return attr
        raise AttributeError(f"Конфигурация не содержит поле '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value
    
    def save(self) -> None:
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=4, ensure_ascii=False)


conf = Config()