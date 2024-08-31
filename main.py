import pygame as pg
import sys
import numpy as np
from scipy.stats import linregress

# edit these constants
SLOPE_F = 1 # slope of the function F which is the mean of the function around which points are generated via a normal distribution
Y_INTERCEPT_F = 0 # y-intercept of the function F
NORMAL_DISTRIBUTION_STD = 80 # standard deviation of the normal distribution from which points are generated
NUM_POINTS = 30 # number of points shown, including your cursor

WINDOW_SIZE = (800, 800) # size of window in pixels
AXIS_SIZE = (600, 600) # size of axis in pixels
AXIS_OFFSET = (100, 100) # offset of axis from the edge of the window

# colors (RGB codes)
BACKGROUND_COLOR = (0, 0, 0)
AXIS_COLOR = (255, 255, 255)
POINT_COLOR = (200, 200, 255)
LSRL_COLOR = (0, 128, 255)
CURSOR_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)

# defines and stores global values for the slope (m) and y-intercept (b) of the function F
def setF(slope, yIntercept):
    global m, b

    m = slope
    b = yIntercept

# calculates f(x) for a given x using the globals previously defined
def f(x):
    return m * x + b

# generates random x value, and a random y value normally distributed away from the true y value for said x
def generateRandomPoint(function, std):
    x = np.random.rand() * AXIS_SIZE[0]
    y = function(x) + np.random.default_rng().normal(0, std)

    # recalculates points that are out of the dimensions of teh graph
    while y < 0 or y > AXIS_SIZE[1]:
        x = np.random.rand() * AXIS_SIZE[0]
        y = function(x) + np.random.default_rng().normal(0, std)

    return (x, y)

# calculates the LSRL using numpy
def calculateLSRL(points):
    [xValues, yValues] = np.transpose(points)

    return linregress(xValues, yValues)

# calculates the starting and ending points of the LSRL for plotting purposes
def calculateLSRLBoundaryPoints(lsrl):
    slope = lsrl.slope
    yIntercept = lsrl.intercept

    (x1, y1) = (0, yIntercept)
    (x2, y2) = (AXIS_SIZE[0], slope * AXIS_SIZE[0] + yIntercept)

    if y1 < 0:
        (x1, y1) = (-yIntercept / slope, 0)
    if y2 > AXIS_SIZE[1]:
        (x2, y2) = ((AXIS_SIZE[1] - yIntercept) / slope, AXIS_SIZE[1])

    return [(x1, y1), (x2, y2)]

# converts cartesian coordinates of the displayed axis (origin in bottom left, offset) to screen coordinates (origin in top left)
def cartesianToScreenCoordinates(cartesianCoordinates):
    (x, y) = cartesianCoordinates

    return (x + AXIS_OFFSET[0], -y + AXIS_SIZE[1] + AXIS_OFFSET[1])

# opposite of prior function
def screenToCartesianCoordinates(screenCoordinates):
    (x, y) = screenCoordinates

    return (x - AXIS_OFFSET[0], -y + AXIS_SIZE[1] + AXIS_OFFSET[1])

# initializes pygame window and clock with preset parameters and backgroud color
def initializeWindow(windowSize, backgroundColor):
    pg.init()

    window = pg.display.set_mode(windowSize)
    pg.display.set_caption("LSRL Simulation")
    window.fill(backgroundColor)

    clock = pg.time.Clock()

    return [window, clock]

# used to reset the windows background/contents
def drawBackground(window, backgroundColor):
    window.fill(backgroundColor)

# draws the axis
def drawAxis(window, axisSize, axisColor, axisOffset):
    pg.draw.line(window, axisColor, (axisOffset[0], axisOffset[1]), (axisOffset[0], axisOffset[1] + axisSize[1]), 2)
    pg.draw.line(window, axisColor, (axisOffset[0], axisOffset[1] + axisSize[1]), (axisOffset[0] + axisSize[0], axisOffset[1] + axisSize[1]), 2)

# draws the distribution of points on the window
def drawPoints(window, points, pointColor):
    for point in points:
        pg.draw.circle(window, pointColor, cartesianToScreenCoordinates(point), 3)

# draws the LSRL on the window
def drawLSRL(window, lsrlBoundaryPoints, lsrlColor):
    pg.draw.line(window, lsrlColor, cartesianToScreenCoordinates(lsrlBoundaryPoints[0]), cartesianToScreenCoordinates(lsrlBoundaryPoints[1]), 3)

# draws the point that is underneath the cursor
def drawCursorPoint(window, cursorColor):
    cursorX, cursorY = pg.mouse.get_pos()

    pg.draw.circle(window, cursorColor, (cursorX, cursorY), 7)

    return (cursorX, cursorY)

# writes the LSRL info (slope, y-int, r-value, p-value, and standard error) on the window
def drawLSRLInfo(window, lsrl, textColor):
    font = pg.font.Font(None, 24)

    slope = lsrl.slope
    yIntercept = lsrl.intercept
    rValue = lsrl.rvalue
    pValue = lsrl.pvalue
    stdErr = lsrl.stderr

    slopeText = font.render("Slope: " + str(round(slope, 4)), True, textColor)
    yInterceptText = font.render("Y-Intercept: " + str(round(yIntercept, 4)), True, textColor)
    rValueText = font.render("R-Value: " + str(round(rValue, 4)), True, textColor)
    pValueText = font.render("P-Value: " + str(round(pValue, 4)), True, textColor)
    stdErrText = font.render("Standard Error: " + str(round(stdErr, 4)), True, textColor)

    window.blit(slopeText, (WINDOW_SIZE[0] - 200, 10))
    window.blit(yInterceptText, (WINDOW_SIZE[0] - 200, 35))
    window.blit(rValueText, (WINDOW_SIZE[0] - 200, 60))
    window.blit(pValueText, (WINDOW_SIZE[0] - 200, 85))
    window.blit(stdErrText, (WINDOW_SIZE[0] - 200, 110))

# sets the slope and y-int from the constants
setF(SLOPE_F, Y_INTERCEPT_F)

points = []

# generates distribution using the generateRandomPoint function and adds them to the list 
for i in range(NUM_POINTS):
    point = generateRandomPoint(f, NORMAL_DISTRIBUTION_STD)
    points.append(point)

# starts window/clock
[window, clock] = initializeWindow(WINDOW_SIZE, BACKGROUND_COLOR)

# the main loop, runs the real-time simulation
while True:
    drawBackground(window, BACKGROUND_COLOR)

    drawAxis(window, AXIS_SIZE, AXIS_COLOR, AXIS_OFFSET)

    drawPoints(window, points, POINT_COLOR)

    cursorPosition = drawCursorPoint(window, CURSOR_COLOR)

    # adding cursor point to a new array so the LSRL can be calculated including the cursor location
    pointsAndCursor = points + [screenToCartesianCoordinates(cursorPosition)]

    lsrl = calculateLSRL(pointsAndCursor)

    lsrlBoundaryPoints = calculateLSRLBoundaryPoints(lsrl)

    drawLSRL(window, lsrlBoundaryPoints, LSRL_COLOR)

    drawLSRLInfo(window, lsrl, TEXT_COLOR)

    # allows soft quitting using the red X button rather than control C
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

    # pushes new data to the window
    pg.display.flip()

    # controls framerate
    clock.tick(60)