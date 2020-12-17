import copy
from pathlib import Path


class Polygon:
    # Id = -1
    # points = []  # list of Point2D
    # insidePolygons = []  # List of List of Point2D
    # label = ""

    def __init__(self, id, points=[], insidePoints=[], label=""):
        self.Id = id
        self.points = points.copy()
        self.insidePolygons = insidePoints.copy()
        self.label = label

    @staticmethod
    def getStrPoints(polygonPoints):
        outSrt = f"Poly_coordinates: {len(polygonPoints)} "

        for point in polygonPoints:
            outSrt += f"[{point[0]}; {point[1]}],"
        else:
            outSrt = outSrt[0:-1]  # Remove last ","

        return outSrt


class MarkupFrame:
    # imageName = ""
    # polygons = []  # list of Polygon Class

    def __init__(self, imageName="", polygons=[]):
        self.imageName = imageName
        self.polygons = polygons.copy()

    def getPolygonById(self, polygonId):
        for iter, polyItem in enumerate(self.polygons):
            if polyItem.Id == polygonId:
                return self.polygons[iter]

        return None


class PolygonMarkup:
    # markup_fn = ""
    # markup = []  # list of MarkupFrame

    def addFrame(self, newFrame):
        pass

    def __init__(self, markup_fn="", nowLoad=True):
        self.markup_fn = markup_fn
        self.markup = []

        if nowLoad:
            if markup_fn == "":
                raise Exception(" PolygonMarkup.__init__()\n PolygonMarkup.Load() markup_fn not be empty ")

            self.load(markup_fn)

    def load(self, markup_fn):
        markup_f = open(markup_fn, "r")
        self.markup_fn = markup_fn
        frameIter = -1

        for line in markup_f.readlines():
            if line.strip() == "": continue

            linePart = line.split()
            if linePart[0] in "Frame_width:":
                continue

            elif linePart[0] in "Frame_name:":
                frameNameParts = linePart[1:-2]
                frameName = ""
                for namePart in frameNameParts:
                    frameName += f" {namePart}"
                else:
                    frameName.lstrip()
                    self.markup.append(MarkupFrame(frameName, []))
                    frameIter += 1

            elif linePart[0] in "Poly_id:":
                id = int(linePart[1])
                points = []

                polygonPointParts = line.split(",")
                polygonPointParts[0] = polygonPointParts[0].split("[")[1]
                polygonPointParts[-1] = polygonPointParts[-1].split("]")[0]
                for polygonPointPart in polygonPointParts:
                    p1, p2 = polygonPointPart.strip("[,]").split(";")
                    points.append([int(p1), int(p2)])

                label = linePart[-1]

                self.markup[frameIter].polygons.append(Polygon(id, points, [], label))

            elif linePart[0] in "rootPoly_id:":
                if linePart[3] == "0": continue
                rootPolyId = int(linePart[1])
                rootPolygon = self.markup[frameIter].getPolygonById(rootPolyId)

                newPolygon = []
                polygonPointParts = line.split(",")
                polygonPointParts[0] = polygonPointParts[0].split("[")[1]
                polygonPointParts[-1] = polygonPointParts[-1].split("]")[0]
                for polygonPointPart in polygonPointParts:
                    p1, p2 = polygonPointPart.strip("[,]").split(";")
                    newPolygon.append([int(p1), int(p2)])

                rootPolygon.insidePolygons.append(newPolygon)

    def save(self, newMarkup_fn):
        newMarkup = open(newMarkup_fn, "w")

        newMarkup.write("Frame_width: 0 Frame_height: 0 First_frame_name: imageStart Last_frame_name: imageEnd\n")

        frameIter = 1
        for frame in self.markup:
            newMarkup.write(f"Frame_name: {frame.imageName.strip()} Frame_number: {frameIter}\n")

            for polygon in frame.polygons:
                newMarkup.write(
                    f"Poly_id: {polygon.Id} {Polygon.getStrPoints(polygon.points)} Poly_label: {polygon.label}\n")

                for insidePolygon in polygon.insidePolygons:
                    newMarkup.write(
                        f"rootPoly_id: {polygon.Id} {Polygon.getStrPoints(insidePolygon)} Poly_label: _background_\n")

            frameIter += 1

        newMarkup.close()

    def containsFrameName(self, findName):
        for frame in self.markup:
            if findName == frame.imageName:
                return True

        return False

    def getFrameByFrameName(self, findName):
        for iter, frame in enumerate(self.markup):
            if findName is frame.ImageName:
                return self.markup[iter]

        return None

    def idFix(self):
        polygonId_iter = 0
        for frame in self.markup:
            for polygon in frame.polygons:
                polygon.Id = polygonId_iter
                polygonId_iter += 1


def mergeMarkups(ListPolygonMarkup):
    # merge any PolygonMarkup
    # fix only poly_id
    # return new PolygonMarkup

    outMarkup = PolygonMarkup("", False)

    for polygonMarkup in ListPolygonMarkup:
        outMarkup.markup += copy.deepcopy(polygonMarkup.markup)

    outMarkup.idFix()
    return outMarkup


def mergeAllMarcups(headFolder, outMarkup_fn, findMask="**", ):
    # find all *.txt files and merge

    markupsPath = list(Path(headFolder).glob(findMask + ".txt"))

    listOfPolygonMarkup = []
    for markupPath in markupsPath:
        listOfPolygonMarkup.append(PolygonMarkup(markupPath))

    outMarkup = mergeMarkups(listOfPolygonMarkup)
    outMarkup.save(outMarkup_fn)


def mergeCorrectAndUncorrectMarkups(correctMarkup, unCorrectMarkups, genUnique=False):
    if genUnique:
        outMarkup = PolygonMarkup("", False)
    else:
        outMarkup = copy.deepcopy(correctMarkup)

    for unCorrectFrame in unCorrectMarkups.markup:
        if correctMarkup.containsFrameName(unCorrectFrame.imageName):
            pass
        else:
            outMarkup.markup.append(unCorrectFrame)

    outMarkup.idFix()
    return outMarkup


# start
if __name__ == '__main__':
    inPath = r"H:\ImagesSplitter"
    folders = ("Land", "Object", "Sky")

    for folder in folders:
        outPath = r"H:\ImagesSplitter" + "/" + folder + ".txt"
        mergeAllMarcups(inPath, outPath, "*/*" + folder + "*")

# end

# correct_polygon_markup = PolygonMarkup(r"H:\dataset\CMI_MGU\dataset_2\corr.txt")
# unCorrect_polygon_markup = PolygonMarkup(r"H:\dataset\CMI_MGU\dataset_2\unCorr.txt")


# out_polygon_markup = mergeMarkups((correct_polygon_markup, unCorrect_polygon_markup))
# out_polygon_markup.save(out_path + "fullMerge.txt")
#
# out_polygon_markup = mergeCorrectAndUncorrectMarkups(correct_polygon_markup, unCorrect_polygon_markup, True)
# out_polygon_markup.save(out_path + "uniqueMerge.txt")
#
# out_polygon_markup = mergeCorrectAndUncorrectMarkups(correct_polygon_markup, unCorrect_polygon_markup, False)
# out_polygon_markup.save(out_path + "oldAndNewMerge.txt")
