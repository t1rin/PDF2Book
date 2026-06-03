# PDF2Book

Программа, позволяющая распределять страницы PDF в таком порядке, чтобы при распечатке можно было сложить книжку из блоков по 2 страницы исходного документа

<img src="src/1.png" ></img>

# Описание

- `core` - модуль реализации логики программы

- `ui` - модуль реализации пользовательского интерфейса

## Модуль `core`

### Методы класса `PDFImposer()`

#### `PDFImposer().load_doc(path)`

загружает исходный файл PDF

#### `PDFImposer().update_params(rows=2, cols=2, margin=2, cut_lines=True, cut_color=(0.5, 0.5, 0.5), blocks_are_vertical=False)`

обновляет параметры расшивки

#### `PDFImposer().get_preview(page_num, scale=1)`

позволяет получить набор данных страницы `page_num` итогового документа без экспорта

#### `PDFImposer().update_doc()`

пересчитывает выходной документ по параметрам

#### `PDFImposer().export_doc(path)`

сохраняет выходной файл

## Модуль `ui`

позволяет взаимодействовать с `PDFImposer()` посредствам пользовательского интерфейса

UI реализован с помощью модуля `dearpygui`

# Подключение

## 1. Создание виртуального окружения внутри каталога проекта

```shell
python3 -m venv venv
```

## 2. Подключение к виртуальному окружению

### Linux

```shell
source ./venv/bin/activate
```

или

### Windows

```shell
venv\Scripts\activate
```

## 3. Установка зависимостей

```shell
pip install -r requirements.txt
```

# Пример

получение документа для печати и сборки книжки:

```python
from core import PDFImposer


pi = PDFImposer()
pi.update_params(margin=0, rows=4)
pi.load_doc("input.pdf")
pi.export_doc("output.pdf")
```


