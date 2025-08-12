from openpyxl import Workbook
from openpyxl.cell.cell import KNOWN_TYPES
from scrapy.exporters import BaseItemExporter
from scrapy.utils.project import get_project_settings


class XlsxItemExporter(BaseItemExporter):
    """XlsxItemExporter allows exporting the output items to a XLSX file."""

    def __init__(self, file, include_header_row=True, join_multivalued=',',
                 default_value=None, **kwargs):
        self._configure(kwargs, dont_fail=True)

        self.file = file
        self.include_header_row = include_header_row
        self._join_multivalued = join_multivalued
        self.default_value = default_value
        self._headers_not_written = True

        self.workbook = Workbook(write_only=True)
        self.sheet = self.workbook.create_sheet()
        self.settings = get_project_settings()

    def serialize_field(self, field, name, value):
        serializer = field.get('serializer', self._default_serializer)
        return serializer(value)

    def _default_serializer(self, value):
        # Do not modify values supported by openpyxl.
        if isinstance(value, KNOWN_TYPES):
            return value

        # Convert lists and tuples of strings into a single string.
        if self._join_multivalued is not None and \
                isinstance(value, (list, tuple)):
            try:
                return self._join_multivalued.join(value)
            except TypeError:
                pass

        # Convert complex types like dict into a string as fallback mechanism.
        return str(value)

    def export_item(self, item):
        if self._headers_not_written:
            self._headers_not_written = False
            self._write_headers_and_set_fields_to_export(item)

        fields = self._get_serialized_fields(item,
                                             default_value=self.default_value,
                                             include_empty=True)
        values = list(value for _, value in fields)
        self.sheet.append(values)

    def finish_exporting(self):
        self.workbook.save(self.file.name)

    def change_name_field(self, name_list):
        temp = []
        field_names = self.settings.get('CUSTOM_FIELDS')
        if field_names:
            for name in name_list:
                if name in field_names:
                    temp.append(field_names[name])
                else:
                    temp.append(name)
            return temp
        else:
            return name_list

    def _write_headers_and_set_fields_to_export(self, item):
        if self.fields_to_export is None:
            if isinstance(item, dict):
                self.fields_to_export = list(item.keys())
            else:
                self.fields_to_export = list(item.fields.keys())

        if self.include_header_row:
            row = list(self.fields_to_export)
            self.sheet.append(self.change_name_field(row))
