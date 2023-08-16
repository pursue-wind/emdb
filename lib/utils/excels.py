import openpyxl


def read_excel(file_path, sheet_name):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb[sheet_name]

    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    return data


if __name__ == '__main__':
    file_path = '/Users/van/projects/likn/emdb/docs/movies.xlsx'
    sheet_names = ['companys', 'movies']

    for sheet_name in sheet_names:
        excel_data = read_excel(file_path, sheet_name)
        print(f"Data from {sheet_name}:")
        for row in excel_data:
            print(row)
        print()
