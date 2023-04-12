# importing the module
import cv2
import imutils
import csv
from scrollable import PanZoomWindow
import numpy as np

clicked = False

deaths = []
with open("Deaths.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t")
    for row in rd:
        deaths.append(row)

pumps = []
with open("Pumps.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t")
    for row in rd:
        pumps.append(row)

deaths = [[float(death[1]), float(death[2])] for death in deaths if death[0] != 'Case']
pumps = [[float(pump[1]), float(pump[2])] for pump in pumps if pump[0] != 'Pump']

def get_bounds(row, width, height, radius=1):
    h = (0.119 + ((row[1] - 5) * (0.972 - 0.119) / (18.5 - 5))) * height
    w = (0.339 + ((row[0] - 8.7) * (0.935 - 0.339) / (18.9 - 8.7))) * width
    return (int(w), int(height - h))

def get_point(x, y, width, height):
    return (x / width, y / height)

# function to display the coordinates of
# of the points clicked on the image 
def click_event(event, x, y, flags, params):
  
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
  
        # displaying the coordinates
        # on the Shell
        print(x, ', ', y)
  
        # displaying the coordinates
        # on the image window
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # cv2.putText(img, str(x) + ',' +
        #             str(y), (x,y), font,
        #             1, (255, 0, 0), 2)
        # cv2.imshow('image', img)
        cv2.imshow('image', cv2.circle(img2, (x,y), 2, (0,0,255), 2))
  
    # checking for right mouse clicks     
    if event==cv2.EVENT_RBUTTONDOWN:
  
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
  
        # displaying the coordinates
        # on the image window
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # b = img[y, x, 0]
        # g = img[y, x, 1]
        # r = img[y, x, 2]
        # cv2.putText(img, str(b) + ',' +
        #             str(g) + ',' + str(r),
        #             (x,y), font, 1,
        #             (255, 255, 0), 2)
        # cv2.imshow('image', img)
        cv2.imshow('image', cv2.circle(img2, (x,y), 2, (0,0,255), 2))
  
class EpidemicWindow(PanZoomWindow):
    def __init__(self, img, windowName = 'PanZoomWindow', onLeftClickFunction = None):
        super().__init__(img, windowName, onLeftClickFunction)
        self.trackSquares = {}
        self.tracking = False
        self.corner = None

    def publish(filename="output.csv"):
        with open(filename, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the data rows 
            csvwriter.writerows(rows)
    
    def onMouse(self,event, x,y,_ignore1,_ignore2):
        """ Responds to mouse events within the window. 
        The x and y are pixel coordinates in the image currently being displayed.
        If the user has zoomed in, the image being displayed is a sub-region, so you'll need to
        add self.panAndZoomState.ul to get the coordinates in the full image."""
        if event == cv2.EVENT_MOUSEMOVE:
            return
        elif event == cv2.EVENT_RBUTTONDOWN:
            #record where the user started to right-drag
            self.mButtonDownLoc = np.array([y,x])
        elif event == cv2.EVENT_RBUTTONUP and self.mButtonDownLoc is not None:
            #the user just finished right-dragging
            dy = y - self.mButtonDownLoc[0]
            pixelsPerDoubling = 0.2*self.panAndZoomState.shape[0] #lower = zoom more
            changeFactor = (1.0+abs(dy)/pixelsPerDoubling)
            changeFactor = min(max(1.0,changeFactor),5.0)
            if changeFactor < 1.05:
                dy = 0 #this was a click, not a draw. So don't zoom, just re-center.
            if dy > 0: #moved down, so zoom out.
                zoomInFactor = 1.0/changeFactor
            else:
                zoomInFactor = changeFactor
#            print("zoomFactor: %s"%zoomFactor)
            self.panAndZoomState.zoom(self.mButtonDownLoc[0], self.mButtonDownLoc[1], zoomInFactor)
        elif event == cv2.EVENT_LBUTTONDOWN:
            print(self.tracking)
            #the user pressed the left button. 
            coordsInDisplayedImage = np.array([y,x])
            if np.any(coordsInDisplayedImage < 0) or np.any(coordsInDisplayedImage > self.panAndZoomState.shape[:2]):
                print("you clicked outside the image area")
            elif self.tracking is False:
                print("Setting")
                coordsInFullImage = self.panAndZoomState.ul + coordsInDisplayedImage
                self.tracking = True
                self.corner = (coordsInFullImage[1], coordsInFullImage[0])
            else:
                self.tracking = False
                # print("you clicked on %s within the zoomed rectangle"%coordsInDisplayedImage)
                coordsInFullImage = self.panAndZoomState.ul + coordsInDisplayedImage
                # print("this is %s in the actual image"%coordsInFullImage)
                # print("INITIAL:", coordsInFullImage)
                self.img = cv2.circle(self.img, (coordsInFullImage[1],coordsInFullImage[0]), 1, (255,255,0), 2)
                self.redrawImage()
                # print("this pixel holds %s, %s"%(self.img[coordsInFullImage[0],coordsInFullImage[1]]))
        elif event == cv2.EVENT_LBUTTONUP:
            print(self.corner)
            if self.tracking:
                coordsInDisplayedImage = np.array([y,x])
                coordsInFullImage = self.panAndZoomState.ul + coordsInDisplayedImage
                contained = [
                    death for death in deaths if 
                    min(self.corner[0], coordsInFullImage[1]) <= death[0] <= max(self.corner[0], coordsInFullImage[1]) and
                    min(self.corner[1], coordsInFullImage[0]) <= death[1] <= max(self.corner[1], coordsInFullImage[0])
                ]

                center = (self.corner[0] + coordsInFullImage[1]) / 2, (self.corner[1] + coordsInFullImage[0] / 2, self.panAndZoomState.shape)

                self.trackSquares[center] = contained

                self.publish()

                self.tracking = False

# driver function
if __name__=="__main__":
  
    # reading the image
    img = cv2.imread('958px-Snow-cholera-map-1.jpg', 1)

    # img2 = imutils.resize(img, width=700)
    width, height, channels = img.shape
    for death in deaths:
        img = cv2.circle(img, get_bounds(death, width, height), 1, (0,0,255), 2)
        
    for pump in pumps:
        img = cv2.circle(img, get_bounds(death, width, height), 2, (255,0,0), 2)
  
    # displaying the image
    # cv2.imshow('image', img2)
  
    # setting mouse handler for the image
    # and calling the click_event() function
    # cv2.setMouseCallback('image', click_event)

    window = EpidemicWindow(img, "test window")
    key = -1
    while key != ord('q') and key != 27: # 27 = escape key
        #the OpenCV window won't display until you call cv2.waitKey()
        key = cv2.waitKey(5) #User can press 'q' or ESC to exit.
    cv2.destroyAllWindows()
  
    # # wait for a key to be pressed to exit
    # cv2.waitKey(0)
  
    # # close the window
    # cv2.destroyAllWindows()