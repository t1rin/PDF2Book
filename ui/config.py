import json
import os

from utils import resource_path


class Config:    
    def __init__(self, json_path='config.json'):
        self._path = resource_path(json_path)
        self._data = self._load()
    
    def _load(self):
        if os.path.exists(self._path):
            with open(self._path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else: return {}
    
    def __getattr__(self, name):
        if name in self._data:
            if name == "selected_font":
                return resource_path(self._data[name])
            return self._data[name]
        raise AttributeError(f"Конфигурация не содержит поле '{name}'")
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value
    
    def save(self):
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=4, ensure_ascii=False)


conf = Config()