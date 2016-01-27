import json

from flask import current_app

import gspread
from oauth2client.client import SignedJwtAssertionCredentials


class Sheet(object):
    _fields = None
    records = []

    def __init__(self, *args, **kwargs):
        json_key = json.load(open('client_secret.json'))
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = SignedJwtAssertionCredentials(
            json_key['client_email'], json_key['private_key'].encode(), scope)
        self.gc = gspread.authorize(credentials)
        return super(Sheet, self).__init__(*args, **kwargs)

    def get_sheet(self, gc):
        docs = self.gc.openall()
        for doc in docs:
            if doc.title.find("Copy") > -1 and current_app.config['DEBUG']:
                break
        return doc.sheet1

    def refresh(self):
        if not getattr(self, "sheet", None):
            self.sheet = self.get_sheet(self.gc)
        self.records = self.get_records()

    def get_records(self):
        return self.sheet.get_all_records()

    def get_by_email(self, email):
        row = self.row_by_email(email)
        if row:
            return self.player_by_row(row)

    def row_by_email(self, email):
        cell_list = self.sheet.findall(email)
        if cell_list:
            return cell_list[0].row

    def player_by_row(self, row):
        values = self.sheet.row_values(row)
        return {field: value for field, value in zip(self.fields, values)
                if value}

    def update(self, **data):
        data = self.clean_data(**data)
        row = self.row_from_data(**data)
        if row:
            fields = self.fields
            for k, v in data.items():
                try:
                    column = fields.index(k) + 1
                except ValueError:
                    continue
                else:
                    self.sheet.update_cell(row, column, v)

    def row_from_data(self, **data):
        email = data.pop('email', None)
        if email:
            return self.row_by_email(email)

    def get_field_values(self, field):
        column = self.column_by_field(field)
        return [v for v in self.sheet.col_values(column)[1:] if v]

    def column_by_field(self, field):
        return self.fields.index(field) + 1

    @property
    def fields(self):
        if not self._fields:
            self._fields = [v for v in self.sheet.row_values(1) if v]
        return self._fields

    def clean_data(self, **data):
        return {k: v[0] if isinstance(v, list) else v for k, v in data.items()}
