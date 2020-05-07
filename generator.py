import logging
from random import randint
from typing import List, Union


class Cell:
    def __init__(self, x, y, data, style):
        self.x = x
        self.y = y
        self.data = data
        self.style = style

    def __str__(self):
        return "Cell({}: {} - {})".format(self.x, self.y, self.data)


class Base:
    def __init__(self, row_field: str, header: str):
        self.row_field = row_field
        self.header = header

    @property
    def is_flat_field(self):
        return True

    @property
    def is_row_header(self):
        return False

    @property
    def is_table(self):
        return False

    @property
    def is_table_header(self):
        return False

    @property
    def is_container(self):
        return False

    def process_value(self, *args, **kwargs) -> Union[List[Cell], Cell]:
        pass


class Generator(Base):
    def __init__(
            self,
            schema,
            header,
            is_table,
            row_field,
            is_row_header,
            is_container,
            head=False,
            parent=None,
    ):
        self.schema = schema
        self.current_row = None
        self.x = 0
        self.y = 0
        self.max_x = 0
        self.max_y = 0
        self.fields_generators: List[Base] = []
        self.parent = parent
        self.parents_rows = []  # TODO
        self.transpose = False
        self.header = header
        self._is_table = is_table
        self._is_row_header = is_row_header
        self._is_container = is_container
        self.id = randint(1, 100000)
        self.row_header_exists = False
        self.head = head
        self.children = []
        super(Generator, self).__init__(row_field, header)

    @property
    def is_flat_field(self):
        return False

    @property
    def is_row_header(self):
        return self._is_row_header

    @property
    def is_table(self):
        return self._is_table

    @property
    def is_container(self):
        return self._is_container

    def __str__(self):
        return f"Generator(id: {self.id}, x: {self.x}, y: {self.y})"

    def process_flat_field(self, field_generator, row):
        cell = field_generator.process_value(
            self.x, self.y, row[field_generator.row_field]
        )
        logging.debug("%s from %s", cell, generator)
        yield cell
        self.max_x = max(self.max_x, cell.x)
        self.y += 1
        self.max_y = max(self.max_y, cell.y)

    def process_container(self, field_generator, row):
        for cell in field_generator.process_value(
                row[field_generator.row_field]
        ):
            logging.debug(
                "%s summed y %s, result: y: %s",
                cell,
                generator,
                cell.y + self.y,
            )
            cell.y = cell.y + self.y
            if self.row_header_exists:
                cell.x += 1
            yield cell
            self.max_x = max(self.max_x, cell.x)
            self.max_y = max(self.max_y, cell.y)

    def process_row_header(self, field_generator, row):
        for cell in field_generator.process_value(
                row[field_generator.row_field]
        ):
            yield cell
            self.max_x = max(self.max_x, cell.x)

    def process_table(self, field_generator, row):
        # TODO: Test with two fields
        for inner_row in row[field_generator.row_field]:
            for cell in field_generator.process_value(
                    inner_row
            ):
                self.max_y += 1
                cell.y += self.max_y
                yield cell
                self.max_x = max(self.max_x, cell.x)
                self.max_y = max(self.max_y, cell.y)
                self.y += 1

    def process_value(self, row):
        self.max_x = self.x
        self.max_y = self.y
        if self.row_header_exists:
            self.x += 1
        for field_generator in self.fields_generators:
            if field_generator.is_flat_field:
                yield from self.process_flat_field(field_generator, row)
            elif field_generator.is_container:
                yield from self.process_container(field_generator, row)
            elif field_generator.is_row_header:
                yield from self.process_row_header(field_generator, row)
            elif field_generator.is_table:
                yield from self.process_table(field_generator, row)
        self.x = self.max_x + 1
        if self.head:
            self.shift_x(self.x)
        self.y = 0

    def shift_x(self, x):
        for child in self.children:
            child.x = x
            child.shift_x(x)

    def generate_field_from_schema(self):
        for field in self.schema:
            if field["type"] not in ["table", "container", "row_header"]:
                self.fields_generators.append(
                    fields_map[field["type"]](
                        field.get("header"),
                        field.get("requires_row"),
                        field.get("row_field"),
                    )
                )
            else:
                if not self.row_header_exists:
                    self.row_header_exists = field["type"] == "row_header"
                g = Generator(
                    field["fields"],
                    field.get("header"),
                    field["type"] == "table",
                    field.get("row_field"),
                    field["type"] == "row_header",
                    field["type"] == "container",
                    parent=self.parent,
                )
                g.generate_field_from_schema()
                self.children.append(g)
                self.fields_generators.append(g)


class IntegerField(Base):
    def __init__(self, header, requires_row, row_field):
        self.requires_row = requires_row
        super(IntegerField, self).__init__(row_field, header)

    def get_header(self, x, y, row_data, parents_rows=None):
        return x, y, self.header, None

    def process_value(self, x, y, row_data, parents_rows=None):
        return Cell(x, y, row_data, None)


class StringField(IntegerField):
    def process_value(self, x, y, row_data, parents_rows=None):
        return Cell(x, y, row_data, None)


rows = [
    {
        "id": 1,
        "test5": "test5",
        "test": {
            "test1": "test1",
            "test2": "test2",
            "test3": "test3",
            "test4": "test4",
            "test": {"test1": "test_row_header_1", "test2": "test_row_header_2"},
        },
        "test_table": [
            {"test_table_f1": "ttf1"},
            {"test_table_f1": "ttf1"},
            {"test_table_f1": "ttf1"},
        ]
    },
    {
        "id": 1,
        "test5": "test5",
        "test": {
            "test1": "test1",
            "test2": "test2",
            "test3": "test3",
            "test4": "test4",
            "test": {"test1": "test_row_header_1", "test2": "test_row_header_2"},
        },
        "test_table": [
            {"test_table_f1": "ttf1"},
            {"test_table_f1": "ttf1"},
            {"test_table_f1": "ttf1"},
        ]
    },
    {
        "id": 1,
        "test5": "test5",
        "test": {
            "test1": "test1",
            "test2": "test2",
            "test3": "test3",
            "test4": "test4",
            "test": {"test1": "test_row_header_1", "test2": "test_row_header_2"},
        },
        "test_table": [
            {"test_table_f1": "ttf1"},
            {"test_table_f1": "ttf1"},
            {"test_table_f1": "ttf1"},
        ]
    },
]

fields_map = {"integer": IntegerField, "string": StringField}

result = []
generator = Generator(
    schema=[
        {"row_field": "id", "type": "integer"},
        {"row_field": "test5", "type": "string"},
        {
            "row_field": "test",
            "type": "container",
            "fields": [
                {"row_field": "test1", "type": "string"},
                {"row_field": "test2", "type": "string"},
                {"row_field": "test3", "type": "string"},
                {"row_field": "test4", "type": "string"},
                {
                    "row_field": "test",
                    "type": "row_header",
                    "fields": [
                        {"row_field": "test1", "type": "string"},
                        {"row_field": "test2", "type": "string"},
                    ],
                },
            ],
        },
        {
            "row_field": "test_table",
            "type": "table",
            "fields": [
                {"row_field": "test_table_f1", "type": "string"},
            ]
        }
    ],
    header=None,
    is_table=False,
    row_field=None,
    is_row_header=False,
    head=True,
    is_container=True,
)
# logging.basicConfig(level="DEBUG")
generator.generate_field_from_schema()
for row_ in rows:
    for cell_ in generator.process_value(row_):
        print(cell_)
    print("-" * 8)

# TODO: implement table entity
# TODO: implement "transpose" key
# TODO: add table headers
# TODO: mypy
# TODO: add row_data support
# TODO: tests
# TODO: refactor: too many class vars, they look pretty ugly
# TODO: rework to iterative generation (is it possible for table entity???)
