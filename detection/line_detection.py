import cv2
import numpy as np
from collections import Counter


def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def line_detection(image):
    # print('detecting lines')

    # preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    horizontal_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
    vertical_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    # Combine masks and remove lines
    table_mask = cv2.bitwise_or(horizontal_mask, vertical_mask)

    # cv2.imshow("tresh", thresh)
    # cv2.imshow("tablemask", table_mask)
    # cv2.waitKey(0)

    im = image.copy()

    bw_for_horizontal = table_mask.copy()
    bw_for_vertical = table_mask.copy()
    hor = horizontal_lines(im, bw_for_horizontal)
    ver = vertical_lines(im, bw_for_vertical)

    # ###################################################################
    # for x1, y1, x2, y2 in ver:
    #     cv2.line(im, (x1, y1), (x2, y2), (0, 255, 0), 1)
    #
    # for x1, y1, x2, y2 in hor:
    #     cv2.line(im, (x1, y1), (x2, y2), (0, 255, 0), 1)
    #
    # resize = ResizeWithAspectRatio(im, width=1280, height=920)
    # cv2.imshow("full lines", resize)
    # cv2.waitKey(0)
    # #######################################################################

    return hor, ver


def horizontal_lines(img, horizontal):
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))

    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    horizontal = cv2.dilate(horizontal, (1, 1), iterations=5)
    horizontal = cv2.erode(horizontal, (1, 1), iterations=5)

    # highlighted Horizontal lines
    # cv2.imshow("horizontal", horizontal)
    # cv2.waitKey(0)

    # HoughlinesP function to detect horizontal lines
    hor_lines = cv2.HoughLinesP(horizontal, rho=1, theta=np.pi / 180, threshold=100, minLineLength=30, maxLineGap=3)
    if hor_lines is None:
        return None, None
    temp_line = []
    for line in hor_lines:
        for x1, y1, x2, y2 in line:
            temp_line.append([x1, y1 - 5, x2, y2 - 5])

    # Sorting the list of detected lines by Y1
    hor_lines = sorted(temp_line, key=lambda x: x[1])
    # print('hor_lines:', hor_lines)

    lasty1 = -111111
    lines_x1 = []
    lines_x2 = []
    hor = []
    i = 0
    for x1, y1, x2, y2 in hor_lines:
        if lasty1 <= y1 <= lasty1 + 10:
            lines_x1.append(x1)
            lines_x2.append(x2)
        else:
            if i != 0 and len(lines_x1) is not 0:
                hor.append([min(lines_x1), lasty1, max(lines_x2), lasty1])
            lasty1 = y1
            lines_x1 = []
            lines_x2 = []
            lines_x1.append(x1)
            lines_x2.append(x2)
            i += 1
    hor.append([min(lines_x1), lasty1, max(lines_x2), lasty1])

    # print('hor_lines final:', hor)

    # ######################################################
    # for x1, y1, x2, y2 in hor:
    #     cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
    #
    # cv2.imshow("horizontal final", img)
    # cv2.waitKey(0)
    # ######################################################

    return hor


def vertical_lines(img, vertical):
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))

    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    vertical = cv2.dilate(vertical, (1, 1), iterations=8)
    vertical = cv2.erode(vertical, (1, 1), iterations=7)

    # ###############################################
    # cv2.imshow("vertical", vertical)
    # cv2.waitKey(0)
    # ################################################

    # HoughlinesP function to detect vertical lines
    # ver_lines = cv2.HoughLinesP(vertical,rho=1,theta=np.pi/180,threshold=20,minLineLength=20,maxLineGap=2)
    ver_lines = cv2.HoughLinesP(vertical, 1, np.pi / 180, 20, np.array([]), 20, 2)
    if ver_lines is None:
        return None, None
    temp_line = []
    for line in ver_lines:
        for x1, y1, x2, y2 in line:
            temp_line.append([x1, y1, x2, y2])

    ver_lines = sorted(temp_line, key=lambda x: x[0])

    lastx1 = -111111
    lines_y1 = []
    lines_y2 = []
    ver = []
    count = 0
    lasty1 = -11111
    lasty2 = -11111
    for x1, y1, x2, y2 in ver_lines:
        if lastx1 <= x1 <= lastx1 + 15 and not (
                (min(y1, y2) < min(lasty1, lasty2) - 20 or min(y1, y2) < min(lasty1, lasty2) + 20) and (
                (max(y1, y2) < max(lasty1, lasty2) - 20 or max(y1, y2) < max(lasty1, lasty2) + 20))):
            lines_y1.append(y1)
            lines_y2.append(y2)
            # lasty1 = y1
            # lasty2 = y2
        else:
            if count != 0 and len(lines_y1) is not 0:
                ver.append([lastx1, min(lines_y2) - 5, lastx1, max(lines_y1) - 5])
            lastx1 = x1
            lines_y1 = []
            lines_y2 = []
            lines_y1.append(y1)
            lines_y2.append(y2)
            count += 1
            lasty1 = -11111
            lasty2 = -11111
    ver.append([lastx1, min(lines_y2) - 5, lastx1, max(lines_y1) - 5])

    # ##############################################################
    # for x1, y1, x2, y2 in ver:
    #     cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
    #
    # cv2.imshow("vertical final", img)
    # cv2.waitKey(0)
    #######################################################################

    return ver