import xml.etree.ElementTree as ET
import lxml.etree as etree
import itertools
import csv
import cv2
from paddleocr import PaddleOCR, draw_ocr
from detection.extract import extract_table, span


def create_metadata(image):
    table = [10, 10, 1260, 302]
    imag = image.copy()
    final = extract_table(imag)

    ocr = PaddleOCR(lang="en", use_gpu=True)

    if final is None:
        return None
    X = []
    Y = []
    for x1, y1, x2, y2, x3, y3, x4, y4 in final:
        if x1 not in X:
            X.append(x1)
        if x3 not in X:
            X.append(x3)
        if y1 not in Y:
            Y.append(y1)
        if y2 not in Y:
            Y.append(y2)

    X.sort()
    Y.sort()

    tableXML = etree.Element("table")
    Tcoords = etree.Element("Coords", points=str(table[0]) + "," + str(table[1]) + " " + str(table[2]) + "," + str(
        table[3]) + " " + str(table[2]) + "," + str(table[3]) + " " + str(table[2]) + "," + str(table[1]))
    tableXML.append(Tcoords)

    cv2.rectangle(imag, (table[0], table[1]), (table[2], table[3]), (0, 255, 0), 2)
    for box in final:
        # print("box: ", box)
        cv2.rectangle(imag, (box[0], box[1]), (box[6], box[7]),
                      (255, 0, 255), 2)

        roi = imag[box[1]:box[3], box[0]:box[4]]
        results = ocr.ocr(roi, det=True, rec=True)

        # print("results: ", results)
        cell = etree.Element("cell")
        end_col, end_row, start_col, start_row = span(box, X, Y)
        cell.set("end-col", str(end_col))
        cell.set("end-row", str(end_row))
        cell.set("start-col", str(start_col))
        cell.set("start-row", str(start_row))

        one = str(box[0]) + "," + str(box[1])
        two = str(box[2]) + "," + str(box[3])
        three = str(box[4]) + "," + str(box[5])
        four = str(box[6]) + "," + str(box[7])

        coords = etree.Element("Coords", points=one + " " + two + " " + three + " " + four)

        text = ""
        for i, result in enumerate(results):
            for j, res in result:
                if len(res) != 0:
                    text += res[0] + " "
                    # print("text: ", text)

        value = etree.Element("Text", value=text)

        cell.append(coords)
        cell.append(value)
        tableXML.append(cell)

    # cv2.imshow("detected cells", imag)
    # cv2.waitKey(0)

    # print(tableXML)
    return tableXML


def createCSV():
    tree = ET.parse('tableXML.xml')
    root = tree.getroot()

    table = root.find('table')
    # print("table:{}", table)

    rows = []

    for cell in table.findall('.//cell'):
        # print("cell:{}", cell)

        start_row = int(cell.attrib['start-row'])
        end_row = int(cell.attrib['end-row'])
        start_col = int(cell.attrib['start-col'])
        end_col = int(cell.attrib['end-col'])
        text = cell.find('Text').attrib['value']

        while len(rows) <= end_row:
            rows.append([])

        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                while len(rows[row]) <= col:
                    rows[row].append('')
                rows[row][col] = text

    with open('tableCSV.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)