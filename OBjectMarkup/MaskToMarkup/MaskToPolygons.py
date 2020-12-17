import cv2
import numpy as np
import colorsys
from pathlib import Path
from MarkupClasses import *
import copy
import os

imputMaskFolder = r"E:\outSourseMarkups\Stages_Data\Images_for_filter\ProcessedImagesDB_13.0\Masks"
colorScheme_fn = r"E:\outSourseMarkups\Stages_Data\COLOR.txt"
outMarkup_path = r"E:\outSourseMarkups\Stages_Data\Images_for_filter\ProcessedImagesDB_13.0\ProcessedImagesDB_13.0.txt"

colorScheme = {}


def loadColors(color_fn):
    colorScheme_file = open(color_fn, "r")
    for line in colorScheme_file.readlines():
        split_line = line.split(":")
        label = split_line[0]
        str_R, str_G, str_B = split_line[1].strip("(").strip(") ").split(",")
        color_rgb = [int(str_R), int(str_G), int(str_B)]
        colorScheme[label] = color_rgb


loadColors(colorScheme_fn)
MP = PolygonMarkup("", nowLoad=False)

for mask_path in list(Path(imputMaskFolder).glob("*")):
    imageMask_bgr = cv2.imread(str(mask_path))

    print(mask_path)
    # cv2.imshow("imageMask_rgb", imageMask_bgr)
    image_name = os.path.basename(mask_path)
    image_name = image_name.replace("_mask.png","")
    markup_frame = MarkupFrame()
    markup_frame.imageName = image_name

    for colorKey in colorScheme:

        color_rgb = colorScheme[colorKey]
        color_brg = np.array([color_rgb[2], color_rgb[1], color_rgb[0]])

        segmentation_mask = cv2.inRange(imageMask_bgr, color_brg, color_brg)
        #cv2.imshow("segmentation_mask",segmentation_mask)
        #cv2.waitKey(1)

        # clear garbage
        segmentation_mask = cv2.morphologyEx(segmentation_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        segmentation_mask = cv2.morphologyEx(segmentation_mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
        segmentation_mask = cv2.morphologyEx(segmentation_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        contours, hierarchy = cv2.findContours(segmentation_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)

        approxCountor = []
        for countor in contours:
            epsilon = 0.002 * cv2.arcLength(countor, True)
            approxCountor.append(cv2.approxPolyDP(countor, epsilon, True))
        contours = approxCountor

        for counter in contours:
            if len(counter) > 3:
                polygon = Polygon(-1)
                polygon.label = colorKey

                points = []
                for point in counter.tolist():
                    points.append([point[0][0], point[0][1]])

                polygon.points = points
                markup_frame.polygons.append(polygon)
                del polygon
        
		#polygon_img = imageMask_bgr.copy()
        #polygon_img[:] = np.array([0, 0, 0])

        #cv2.fillPoly(polygon_img, pts=contours, color=[color_rgb[2], color_rgb[1], color_rgb[0]])

        #if len(contours) > 0:
        #    iter = 0
        #    for component in zip(contours, hierarchy[0]):
        #        currentContour = contours[iter]
        #        currentHierarchy = component[1]
		#
        #        if currentHierarchy[2] < 0:
        #            # these are the innermost child components
        #            cv2.polylines(polygon_img, [currentContour], True, [0, 0, 255], 2)
        #        elif currentHierarchy[3] < 0:
        #            # these are the outermost parent components
        #            cv2.polylines(polygon_img, [currentContour], True, [0, 255, 0], 2)
		#
        #       iter += 1

        #cv2.imshow("polygon_" + colorKey, polygon_img)
        #cv2.waitKey()
        #cv2.destroyWindow("polygon_" + colorKey)

    MP.markup.append(markup_frame)
    del markup_frame

print("save.")
MP.idFix()
MP.save(outMarkup_path)
print("done")
