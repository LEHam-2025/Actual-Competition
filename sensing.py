'''
The library for sensing functions. 
Imports from math and sr.robot3, and is imported by the movement library.
This is the first file in the chain.
'''

from math import inf
from math import sin
from sr.robot3 import *

r = Robot(wait_for_start = False)

#The respective boards of the robot

MOTOR1 = r.motor_boards["SR0HDM"]
MOTOR2 = r.motor_boards["SR0NBL"]

SERVOS = r.servo_board.servos #There is only one servo, which controls the arm
POWER = r.power_board.outputs #There is only one non-standard connection, in position H0, which controls the vacuum
CAMERA = r.camera
ARDUINO = r.arduino

MEANS = [ #The categories of marker ids. In the form ['first id', 'last id', Group No, Group Name]
[0, 28, 0, 'bound'], #Boundary
[100, 120, 1, 'z0'], #zone 0 pallets
[120, 140, 2, 'z1'], #zone 1 pallets
[140, 160, 3, 'z2'], #zone 2 pallets
[160, 180, 4, 'z3'], #zone 3 pallets
[195, 199, 5, 'mid rise'], #high rises
[199, 200, 6, 'high rise']] #centre high rise

##Pins##      (trig, echo)
#front_ultra = (3, 4)   
#left_ultra = (6, 7)
#right_ultra = (12, 13)
#back_ultra = (10, 11)

CAM_HEIGHT = 0          #Remember to update with the camera height
myZone = 'z' + str(r.zone)

r.wait_start()          #Initialise stuff and then wait for the start button to be pressed

def free_space(threshold: int = 500) -> list[str]:
    '''
    Returns a list with strings of all the directions that are unblocked.
    \nIf threshold is given, passes that to the is_space
    function
    '''
    return [direction for direction in ['front', 'back', 'left', 'right'] if is_space(direction, threshold)]

def is_space(direction: str, threshold: int = 500) -> bool:
    '''
    Returns a boolean value of whether there is enough space in a certain direction.
    \nThe threshold defaults to 500mm
    '''
    match direction:
        case 'front':
            return front_space() >= threshold
        case 'back':
            return back_space() >= threshold
        case 'left':
            return left_space() >= threshold
        case 'right':
            return right_space() >= threshold
        case _:
            print('Not a direction')
            return False

def front_space() -> int:
    '''
    Returns an integer with the unobscured distance, in mm, in front of the robot.
    \nThis considers the front ultrasound and the camera
    '''

    ultra_dist = ARDUINO.ultrasound_measure(4, 3)
    if not ultra_dist:
        ultra_dist = 5750
    
    close = get_markers(floor= False)
    if close:
        cam_dist = close[0].position.distance
    else:
        cam_dist = 5750
    
    return min([ultra_dist, cam_dist])

def back_space() -> int:
    '''
    Returns an integer with the unobscured distance, in mm, behind the robot.
    \nThis considers the rear ultrasound
    '''

    ultra_dist = ARDUINO.ultrasound_measure(11, 10)
    if not ultra_dist:
        ultra_dist = 5750
    
    return ultra_dist

def right_space() -> int:
    '''
    Returns an integer with the unobscured distance, in mm, to the right of the robot.
    \nThis considers the right ultrasound.
    '''

    ultra_dist = ARDUINO.ultrasound_measure(13, 12)
    if not ultra_dist:
        ultra_dist = 5750

    return ultra_dist

def left_space() -> int:
    '''
    Returns an integer with the unobscured distance, in mm, to the left of the robot.
    \nThis considers the left ultrasound.
    '''

    ultra_dist = ARDUINO.ultrasound_measure(7, 6)
    if not ultra_dist:
        ultra_dist = 5750

    return ultra_dist

def stacked(mark1, mark2) -> bool:
    '''
    Returns a boolean value denoting whether two markers are stacked or not.
    \nIt compares their distances, heights and horizontal distances.
    '''

    hoz_tolerance = 0.18
    vert_tolerance = 50
    dist_tolerance = 200

    angles = (mark1.position.horizontal_angle, mark2.position.horizontal_angle)
    distances = (mark1.position.distance, mark2.position.distance)
    heights = (height(mark1), height(mark2))

    if ((max(angles) - min(angles)) < hoz_tolerance) and ((max(heights) - min(heights)) > vert_tolerance) and (max(distances) - min(distances) < dist_tolerance):
        return True
    
    return False

def max_height(stack: list) -> int:
    '''
    Basically a wrapper for the height function.
    \nReturns an integer with the maximum height of a stack by 
    considering the first item in the list, which should be the highest.
    '''
    return height(stack[0])

def id_type(in_id: int, type_out: int = 0) -> (int | str):
    '''
    Returns the marker category
    \ntype_out defaults to 0, which returns an integer for easier handling, 
    but can be set to 1 to return a string representation.
    \nThe list of meanings can be found at the start of the file as MEANS
    '''

    for type in MEANS:
        if in_id in range(type[0], type[1]):
            if type_out == 0:
                return type[2]
            else:
                return type[3]

def get_angle(markerID: int, type: str = 'y') -> float:
    '''
    Returns the yaw angle of the
    first marker spotted that matches the inputted ID.
    \nReturns 10 if the marker is not seen.
    \nWhat this actually means is that if two faces of a marker are seen, only one of them is considered.
    '''
    result: float = 0
    
    try: #This is actually awful practice, but whatever
        for _ in range(3):          #Take an average of three readings to improve accuracy
            markers = CAMERA.see()

            for marker in markers:
                if marker.id == markerID:
                    if type == 'y':
                        result +=  marker.orientation.yaw
                    else:
                        result += marker.position.horizontal_angle
                    break
        if result == 0:
            return 10.0
        return (result/3)
    except: #And it gets worse
        return 10

def get_distance(markerID: int) -> int:
    '''
    Returns the distance in mm to the
    first marker spotted that matches the inputted ID.
    \nReturns inf if the marker is not seen.
    '''
    markers = CAMERA.see()

    for marker in markers:
        if marker.id == markerID:
            return marker.position.distance

    return inf

def dist_sort(marker) -> int:
    '''
    Pretty much just for the sort function. 
    \nReturns the distance to the marker in millimetres by accessing its distance attribute
    '''

    return marker.position.distance

def is_type(marker, type: str = 'Any') -> bool:
    '''
    Returns a boolean saying whether the marker is of a certain type.
    \ntype defaults to Any, meaning it always returns True
    '''

    if type == 'Any':
        return True
    
    if id_type(marker.id, 1) == type:
        return True
    else:
        return False

def height(marker) -> float:
    '''
    Returns the vertical height of a marker using trig.
    \nAdds the camera height so that there are no negatives
    \nDon't worry about all the assumptions.
    '''

    return (sin(marker.position.vertical_angle)*marker.position.distance) + CAM_HEIGHT

def get_markers(type: str = 'Any', floor: bool = True) -> list:
    '''
    Returns a list of the markers seen.
    \nIf type is given, only returns markers of a specific category
    \nfloor defaults to True, only returning grounded markers.
    \nSorts the markers by distance as well; if an unsorted list of markers is needed please use CAMERA.see() directly.
    '''

    markers = CAMERA.see()

    if type != 'Any':
        markers = [marker for marker in markers if is_type(marker, type)]
    if floor == True:
        markers = [marker for marker in markers if height(marker) < 30]
    
    markers.sort(key=dist_sort)
    return markers
