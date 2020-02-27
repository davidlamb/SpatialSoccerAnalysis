from shapely.geometry.point import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
import math

#Moreira, A.J., & Santos, M.Y. (2007). Concave hull: A k-nearest neighbours approach for the computation of the region occupied by a set of points. GRAPP.

class concaveHullSimple(object):
    #See:
    def __init__(self):
        self.point_list = []
        self.k = 3
        self.point_count = 0


    def create_polygon(self,points, k=3):
        print("Current k %s"%k)
        self.point_list = []
        dataset = []

        for pnt in points:
            self.point_list.append(pnt)
            dataset.append(pnt)
        self.point_count = len(self.point_list)
        

        if self.point_count<3:
            return None
        if k>self.point_count:
            return None


        firstPoint = self.find_min_y_point(self.point_list)


        hull = []
        hull.append(firstPoint)
        currentPoint = firstPoint
        self.point_list.remove(firstPoint)
        previousPoint = firstPoint
        step = 2
        cutoff = math.floor(float(len(self.point_list))/2)

        print("Number k: %s"%(k))
        while ((currentPoint != firstPoint) or (step==2)) and (len(self.point_list)>0):
            if step >1000000:
                print("loop kept going")
                return None
            print("Step %s" %(step))

            if step == 5:
                self.point_list.append(firstPoint)
            kNearestPoints = self.get_nearest_neighbors(self.point_list,currentPoint,k)


            cpoints = self.sort_by_angle(kNearestPoints,currentPoint,previousPoint)
            #print len(cpoints)
            cpoint = None
            its = True
            if len(hull) >= 2:
                for cpoint in cpoints:
                    newEdge = LineString([currentPoint,cpoint])
                    startHull = 0
                    if firstPoint.equals(cpoint):
                        print("cpoint equals firstpoint, length of pointList %s"%len(self.point_list))
                        startHull +=1
                    crosses = False
                    for i in range(startHull,len(hull),1):
                        #try:
                        if i == len(hull)-1:
                            #print "last check"
                            tempLine =LineString([hull[i],hull[0]])
                            crosses = newEdge.crosses(tempLine)
                            #print "Crosses back %s"%crosses
                            break
                        tempLine =LineString([hull[i],hull[i+1]])
                        crosses = newEdge.crosses(tempLine)
                        #print "Crosses %s"%(crosses)
                        if crosses == True:
                            break
                            #if cpoint.disjoint(tempLine) == True:
                                #print "Not on Edge"
                            #else:
                                #print "On Edge"
                        #except:
                            #print "error in crosses check"

                    if crosses == False:
                        its = False
                        break

            else:
                its = False
                cpoint = cpoints[0]
            if its == True:
                print("Intersects, probably should increase k")
                newk=k+1
                poly = self.createPolygon(points,newk)
                return poly
            previousPoint = currentPoint
            currentPoint = cpoint
            hull.append(cpoint)
            #for i in range(0,hull.count):
                #print "%s,%s"%(hull[i].X,hull[i].Y)
            self.point_list.remove(currentPoint)
            step+=1
        #hull.append(firstPoint)
        hullPolygon = Polygon(sum(map(list, (p.coords for p in hull)), []))
        #print ("Part count %s" % list(hullPolygon.interior.coords))
        #if len(list(hullPolygon.interior.coords)) > 1:
            #print("Not all points contained increasing k")
            #newk=k+1
            #if newk > len(points)-1:
                #return None
            #poly = self.create_polygon(points,newk)
            #return poly
        contains = True
        #within = True
        #touches = True
        disj = False
        for pnt in dataset:
            contains = hullPolygon.contains(pnt)
            #within = pnt.within(hullPolygon)
            #touches = hullPolygon.touches(pnt)
            disj = hullPolygon.disjoint(pnt)
            #print contains
            if disj==True:
                print("Not all points contained increasing k")
                newk=k+1
                if newk > len(points)-1:
                    print("Exceeds the number of points")
                    return hullPolygon
                poly = self.create_polygon(points,newk)
                return poly

        return hullPolygon


    def find_min_y_point(self, pointList):
        minY = 10000000**10
        minPnt = Point(0,0)
        for pnt in pointList:
            if pnt.y < minY:
                minY = pnt.y
                minPnt = pnt
        return minPnt

    def findMinlrPoint(self, pointList):
        minY = 10000000**10
        maxX = -(10000000**10)
        minPnt = Point(0,0)
        for pnt in pointList:
            if pnt.Y <= minY and pnt.X >= maxX:
                minY = pnt.y
                maxX = pnt.x
                minPnt = pnt
        return minPnt

    def get_nearest_neighbors(self, pointList, point, k):
        distanceList = []
        for i, pnt in enumerate(pointList):
            distanceList.append((self.distance(point,pnt),i))
        distanceList.sort()
        nearest = []
        endLst = min(len(distanceList),k)
        for x in range(0,endLst):
            indx = distanceList[x][1]
            nearest.append(pointList[indx])
        return nearest


    def distance(self,point1,point2):
        dx = point1.x - point2.x
        dy = point1.y - point2.y
        return math.sqrt(dx*dx+dy*dy)

    def sort_by_angle(self,nearest,point,prevPoint):
        angles = []
        for indx,nearestPoint in enumerate(nearest):
            angle1 = math.atan2(prevPoint.y - point.y,prevPoint.x-point.x)
            angle2 = math.atan2(nearestPoint.y - point.y,nearestPoint.x-point.x)
            angleDiff = (180.0 / math.pi * (angle2-angle1))
            angles.append((angleDiff%360,indx))

        angles.sort(reverse=True)
        sortedNearest = []
        for angle, indx in angles:
            sortedNearest.append(nearest[indx])
        return sortedNearest