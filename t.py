import csv

def print_csv_header(hcl_csv_path):
    with open(hcl_csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        print(header)

hcl_csv_path = 'C:\\Users\\SYS\\Downloads\\Report_demo_1_2023-10-03.csv'
print_csv_header(hcl_csv_path)