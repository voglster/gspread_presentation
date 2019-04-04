def patch_gspread():
    import gspread

    def append_rows(self, values, value_input_option="RAW"):
        params = {"valueInputOption": value_input_option}

        body = {"majorDimension": "ROWS", "values": values}

        return self.spreadsheet.values_append(self.title, params, body)

    gspread.Worksheet.append_rows = append_rows
