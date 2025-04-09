'''
This is being worked on. 
Imports from the sensing library 
and is imported by the logic library.

This library also imports from math for calculations
'''




from sensing import *
from math import degrees, cos


DCONST = 0.4 #DRIVE CONSTANT - SPEED OF DRIVING
ACONST = 0.4 #ANGLE CONSTANT - SPEED OF TURN

DTIME = 2.5827 #DRIVE TIME - SEE CODE
ATIME = 0.0135 #TIME TO TURN

BIAS00 = -0.95 #THESE BIASES ARE FOR
BIAS01 = 0.95 #CALIBRATIONS OF THE 
BIAS10 = 1 #MOTORS SO THEY TURN AT
BIAS11 = -1 #THE SAME SPEED

PINIONSERVO = 1 #MAKE ARM GO UP DOWN
ARMSERVO = 0 #CLOSE OPEN ARM



def valid_place(marker):
    mark_tower = tower(marker.id)
    if max_height(mark_tower) < 200:
        return True
    elif id_type(mark_tower[0], 1) != myZone:
        return True
    else:
        return False

def clean(towerIDs):
    towerIDs.sort(key=height, reverse= True)
    ids = []
    final = []

    for mark in towerIDs:
        if mark.id not in ids:
            ids.append(mark.id)
            final.append(mark)
    
    return final

def tower(marker_ID):
    '''Returns all the markers in a stack with the given one, arranged from highest to lowest'''
    marks = search_any(wanted_ID = marker_ID) #Get all markers
    try:
        wanted_mark = [mark for mark in marks if mark.id == marker_ID][0] #The marker being considered
        parts = [mark for mark in marks if stacked(wanted_mark, mark)] + [wanted_mark]
        parts = clean(parts)
        return parts
    
    except IndexError:
        return

def drive(distance, rest=0.1):
    #set both motors to be forward speed
    MOTOR1.motors[0].power = BIAS00 * DCONST
    MOTOR1.motors[1].power = BIAS01 * DCONST
    MOTOR2.motors[0].power = BIAS10 * DCONST
    MOTOR2.motors[1].power = BIAS11 * DCONST
    robot.sleep(distance * DTIME)
    MOTOR1.motors[0].power = 0
    MOTOR1.motors[1].power = 0
    MOTOR2.motors[0].power = 0
    MOTOR2.motors[1].power = 0

def turn(angle, unit = 'd', speed = 0.2):
    MOTOR1.motors[0].power = BIAS00 * ACONST
    MOTOR1.motors[1].power = BIAS01 * ACONST
    MOTOR2.motors[0].power = -BIAS10 * ACONST
    MOTOR2.motors[1].power = -BIAS11 * ACONST
    robot.sleep(angle * ATIME)
    MOTOR1.motors[0].power = 0
    MOTOR1.motors[1].power = 0
    MOTOR2.motors[0].power = 0
    MOTOR2.motors[1].power = 0

def pickup(start_height = None, end_height = None):
    servoBoard.servos[ARMSERVO].position = 0.3
    robot.sleep(4)
    servoBoard.servos[ARMSERVO].position = -0.3
    robot.sleep(6)
    servoBoard.servos[ARMSERVO].position = 0
    servoBoard.servos[PINIONSERVO].position = 1
    robot.sleep(4)
    servoBoard.servos[PINIONSERVO].position = 0
     
def drop(start_height = None):
    servoBoard.servos[ARMSERVO].position = -0.3
    robot.sleep(4)
    servoBoard.servos[ARMSERVO].position = 0
    servoBoard.servos[PINIONSERVO].position = -1
    robot.sleep(4)
    servoBoard.servos[PINIONSERVO].position = 0

def arm_move(new_pos):
    '''
    This function moves the arm to a different height.
    It is pretty much just a wrapper and it only accepts float values between -1 and 1
    '''
    
    SERVOS[0].position = new_pos
    r.sleep(0.1)

def align(marker_ID, accuracy = 0.02, type = 'h'):
    '''
    Aligns the robot wth the marker of inputted ID, 
    to the accuracy of the inputted angle (in radians).
    If no accuracy is given, it defaults to 0.02 (~1 degrees)
    '''
    turned = 0
    angle = get_angle(marker_ID, type=type)
    while abs(angle) > accuracy:
        r.sleep(0.01)
        if angle == 10: #If not seen, turn 15 degrees
            turn(15, speed=1)
            turned += 15

            if turned >= 360:
                return False
        else:
            turn((0.4*(angle)), 'r', 0.1) #Since get_angle returns a radians value
        
        angle = get_angle(marker_ID, type=type)
    
    return True

def drive_towards(marker_ID, dist_from = 3, precision = 0.01):
    '''
    Drives the robot towards a marker and stops
    dist_from away. dist_from defaults to 5.
    '''
    try:
        stop = False
        align(marker_ID, 0.02, 'h')
        r.sleep(0.1)
        dist_remain = get_distance(marker_ID)

        dis = ((dist_remain - dist_from)/255) - 3
        drive(dis)
        
        while not stop:
            r.sleep(0.1)
            if get_angle(marker_ID) > (0.5*precision): #If misaligned
                align(marker_ID, precision, 'h')
            
            dist_remain = get_distance(marker_ID)

            dis = ((dist_remain - dist_from)/255)
            drive(dis)
            
            if (dist_remain - (255*dis)) <= (dist_from + 1): #If too close, the camera does not pick up the marker
                stop = True

    except:
        escape()
        drive_towards(marker_ID, dist_from, precision)

def go_to_pick(marker_ID, s_height = -1, e_height = 1, a_height = 0):
    '''Moves the robot to the marker and picks it up. 
    s_height and e_height are passed to the pickup function
    as start_height and end_height respectively. a_height is the approach height'''

    arm_move(a_height)
    drive_towards(marker_ID, 3, precision=0.005)
    pickup(start_height=s_height, end_height = e_height)

def escape():
    allowed_directions = free_space(1000)
    if 'front' in allowed_directions:
        drive(2)    
    elif 'back' in allowed_directions:
        drive(-2)
    elif 'right' in allowed_directions:
        turn(90)
        drive(2)
    elif 'left' in allowed_directions:
        turn(-90)
        drive(2)
    else:
        print('trapped')

def search_any(type = 'Any', wanted_ID = None, floor = False):
    '''Return a list of markers. 
    If none are seen, turns until at least one is spotted. 
    If a full 360 turn has been completed, move somewhere else.
    If wanted_ID is given, looks for that specific ID.
    If type is given, only considers markers of that type'''

    if wanted_ID != None:
        align(wanted_ID, 0.05)
    
    markers = get_markers(type, floor=floor)

    turned = 0
    while not markers:
        turn(15)
        turned += 15
        markers = get_markers(type)

        if turned == 360:
            return []
    
    return markers
