import cv2
from detection.line_detection import line_detection


def extract_table(table_body):

    temp_lines_hor, temp_lines_ver = line_detection(table_body)
    if len(temp_lines_hor) == 0 or len(temp_lines_ver) == 0:
        return None

    table = table_body.copy()
    x = 0
    y = 0
    k = 0
    points = []

    for x1, y1, x2, y2 in temp_lines_ver:
        point = []
        for x3, y3, x4, y4 in temp_lines_hor:
            try:
                k += 1
                x, y = line_intersection(x1, y1, x2, y2, x3, y3, x4, y4)
                point.append([x, y])
            except:
                continue
        points.append(point)

    # for point in points:
    #     for x, y in point:
    #         cv2.line(table, (x, y), (x, y), (0, 0, 255), 8)

    points = clear_points(points)
    print("intersection Points:", points)

    # cv2.imshow("intersection", table)
    # cv2.waitKey(0)

    # for i, point in enumerate(points):
    # print(point)

    box = []
    flag = 1
    lastCache = []

    for i, row in enumerate(points):
        # print(row)
        limitj = len(row)
        currentVala = []
        for j, col in enumerate(row):

            if j == limitj - 1:
                break
            if i == 0:
                nextcol = row[j + 1]
                # print("nextcol: ", nextcol)
                lastCache.append([col[0], col[1], nextcol[0], nextcol[1], 9999, 9999, 9999, 9999])
            else:
                nextcol = row[j + 1]
                currentVala.append([col[0], col[1], nextcol[0], nextcol[1], 9999, 9999, 9999, 9999])
                # Matching
                flag = 1
                index = []
                for k, last in enumerate(lastCache):

                    if (col[1] == last[1]) and lastCache[k][4] == 9999:
                        lastCache[k][4] = col[0]
                        lastCache[k][5] = col[1]
                        if lastCache[k][4] != 9999 and lastCache[k][6] != 9999:
                            box.append(lastCache[k])
                            index.append(k)
                            flag = 1

                    if (nextcol[1] == last[3]) and lastCache[k][6] == 9999:
                        lastCache[k][6] = nextcol[0]
                        lastCache[k][7] = nextcol[1]
                        if lastCache[k][4] != 9999 and lastCache[k][6] != 9999:
                            box.append(lastCache[k])
                            index.append(k)
                            flag = 1

                    if len(lastCache) != 0:
                        if lastCache[k][4] == 9999 or lastCache[k][6] == 9999:
                            flag = 0
                # print(index)
                for k in index:
                    lastCache.pop(k)
                # transferring
                if flag == 0:
                    for last in lastCache:
                        if last[4] == 9999 or last[6] == 9999:
                            currentVala.append(last)

        if i != 0:
            lastCache = currentVala


    # count = 1
    # for i in box:
    #     cv2.rectangle(table_body, (i[0], i[1]), (i[6], i[7]), (int(i[7] % 255), 0, int(i[0] % 255)), 2)
    #     count += 1
    # print(count)
    # cv2.imshow("cells", table_body)
    # cv2.waitKey(0)
    return box


def line_intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    if ((x1 >= x3 - 5 or x1 >= x3 + 5) and (x1 <= x4 + 5 or x1 <= x4 - 5) and (
            y3 + 8 >= min(y1, y2) or y3 - 5 >= min(y1, y2)) and y3 <= max(y1, y2) + 5):
        return x1, y3


def findX(X, x):
    return X.index(x)


def findY(Y, y):
    return Y.index(y)


def span(box, X, Y):
    start_col = findX(X, box[0])  ## x1
    end_col = findX(X, box[4]) - 1  ## x3
    start_row = findY(Y, box[1])  ## y1
    end_row = findY(Y, box[3]) - 1  ## y2
    return end_col, end_row, start_col, start_row


def clear_points(_all_points):
    removed_noise_points = []

    for points in _all_points:
        new_list = []
        for point in points:
            if len(new_list) == 0:
                new_list.append(point)
                continue
            b = False
            for new_point in new_list:
                if abs(point[1] - new_point[1]) < 5:
                    b = True
                    break
            if not b:
                new_list.append(point)
        removed_noise_points.append(new_list)

    return removed_noise_points
