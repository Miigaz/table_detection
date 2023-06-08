import csv
import json


def convertToJPG(PATH):
    images = convert_from_path(PATH)
    for i in range(len(images)):
        images[i].save('pages/page' + str(i) + '.jpg', 'JPEG')


def CsvToJSON():
    with open('tableCSV.csv', newline='') as csvfile:
        # Create a CSV reader object
        reader = csv.DictReader(csvfile, skipinitialspace=True)

        data = [{'key': i + 1, **row} for i, row in enumerate(reader)]

    all_keys = []
    for dictionary in data:
        for key in dictionary:
            if key not in all_keys:
                all_keys.append(key)

    columns = []
    for key in all_keys:
        if key != "key":
            column = {"title": key, "dataIndex": key}
            columns.append(column)

    response = {"columns": columns, "data": data}
    return json.dumps(response)
