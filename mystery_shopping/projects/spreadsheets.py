from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.styles import Font
from openpyxl.styles import PatternFill

from .models import Evaluation
from .project_statuses import ProjectStatus


class EvaluationSpreadsheet:

    def __init__(self, evaluation=None):
        self.evaluation = evaluation if evaluation else None
        self.header_font_style = Font(name='Arial', size=18, bold=True)
        self.sub_header_font_style = Font(name='Arial', size=16, bold=True)
        self.default_font_style = Font(name='Arial', size=14)
        self.header_height = 26
        self.sub_header_height = 23
        self.default_height_singleline = 22.5
        self.default_height_multiline = 21.5
        self.max_characters_line = 130
        self.big_merged_cell = 0
        self.small_merged_cell = 0
        self.evaluation_xlsx = Workbook()
        self.sheet = self.evaluation_xlsx.active
        self.column, self.row = 1, 1

    def generate_spreadsheet(self):
        if self.evaluation.status in ProjectStatus.EDITABLE_STATUSES:
            self.big_merged_cell = 10
            self.small_merged_cell = 0
        else:
            self.big_merged_cell = 8
            self.small_merged_cell = 2

        self.write_header('Script')
        self.write_sub_header('Title')
        self.write_default(self.evaluation.questionnaire_script.title)
        self.write_sub_header('Description')
        self.write_default(self.evaluation.questionnaire_script.description)

        self.row += 2

        self.write_header('Script')
        self.write_sub_header('Title')
        self.write_default(self.evaluation.questionnaire_script.title)
        self.write_sub_header('Description')
        self.write_default(self.evaluation.questionnaire_script.description)

        return self.evaluation_xlsx

    def write_header(self, text):
        self.sheet.merge_cells(start_row=self.row, end_row=self.row,
                               start_column=self.column,
                               end_column=self.column+(self.big_merged_cell+self.small_merged_cell))
        cell_to_write = self.sheet.cell(row=self.row, column=self.column)
        cell_to_write.font = self.header_font_style
        cell_to_write.fill = PatternFill(fill_type='lightTrellis',
                                         start_color='FFFF0000',
                                         end_color='FFFFFF00')
        cell_to_write.value = text
        self.sheet.row_dimensions[self.row].height = self.header_height
        self.row += 1

    def write_sub_header(self, text):
        self.sheet.merge_cells(start_row=self.row, end_row=self.row,
                               start_column=self.column,
                               end_column=self.column+(self.big_merged_cell+self.small_merged_cell))
        cell_to_write = self.sheet.cell(row=self.row, column=self.column)
        cell_to_write.value = text
        cell_to_write.font = self.sub_header_font_style
        cell_to_write.fill = PatternFill(fill_type='lightTrellis',
                                         start_color='FFFFF000',
                                         end_color='FFFFFFF0')
        self.sheet.row_dimensions[self.row].height = self.sub_header_height
        self.row += 1

    def write_default(self, text):
        self.sheet.merge_cells(start_row=self.row, end_row=self.row,
                               start_column=self.column,
                               end_column=self.column+(self.big_merged_cell+self.small_merged_cell))
        cell_to_write = self.sheet.cell(row=self.row, column=self.column)
        cell_to_write.alignment = Alignment(wrap_text=True, shrink_to_fit=True, )
        cell_to_write.value = text
        cell_to_write.font = self.default_font_style
        rows_to_write = self.calculate_height(cell_to_write.value)
        if rows_to_write == 0:
            height = self.default_height_singleline
        else:
            height = self.default_height_multiline * rows_to_write
        self.sheet.row_dimensions[self.row].height = height
        self.row += 1

    def calculate_height(self, text):
        return int(len(text) / self.max_characters_line)
