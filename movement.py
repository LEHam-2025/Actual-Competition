'''
***FIX SERVO STUFF***

Imports from the sensing library 
and is imported by the logic library.

This library also imports from math for calculations

Kenny: To be honest, a lot of logic ended up here as well.
I don't have the effort to move anything, but I think it would be better to have two files instead of three:
One for sensing and movement and one for logic, basically doing a hardware/software split.

Maneet: the servo was goated inserting sauce now
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

PINION_SERVO = SERVOS[1] #MAKE ARM GO UP DOWN
ARM_SERVO = SERVOS[0] #CLOSE OPEN ARM

arm_open: bool = True       #Whether the arm is open or not
arm_height: float = 0       #A float giving the arm's position on the rack as a fraction

def valid_place(marker) -> bool:
    '''
    Returns a boolean of whether the given marker is somewhere a pallet can be placed.
    \nFinds all the markers in a tower with the given one and returns True if either the
    tower is less than the height of three pallets or if the pallet at the top is not
    ours.
    '''

    mark_tower = tower(marker.id)
    if max_height(mark_tower) < 275:
        return True
    elif id_type(mark_tower[0], 1) != myZone:
        return True
    else:
        return False

def clean(towerMarks: list) -> list:
    '''
    \'Cleans\' the list of markers.
    \nRemoves any duplicates and sorts by height so that the highest marker is at the start of the list
    '''

    towerMarks.sort(key=height, reverse= True) #Sorting by height
    ids = []
    final = []

    for mark in towerMarks:         #Clumsy and inefficient but I can't be bothered to change it
        if mark.id not in ids:
            ids.append(mark.id)
            final.append(mark)
    
    return final

def tower(marker_ID: int) -> list:
    '''
    Returns all the markers in a stack with the given one, arranged from highest to lowest
    '''

    marks = search_any(wanted_ID = marker_ID) #Get all markers
    try:
        wanted_mark = [mark for mark in marks if mark.id == marker_ID][0] #The marker being considered
        parts = [mark for mark in marks if stacked(wanted_mark, mark)] + [wanted_mark]
        parts = clean(parts)
        return parts
    
    except IndexError:
        print(f'marker {marker_ID} was not found. How is this even possible. You should be stuck in search_any')

def drive(distance: float, rest: float = 0.1, speed: float = 0.5) -> None:
    '''
    One of two basic movement functions.
    \nMakes the robot move a distance in meters, either forwards or backwards, in a straight line
    \nThe speed parameter controls what fraction of full speed is used
    \nIt then pauses for a bit to avoid unexpected behaviour
    '''

    if distance >= 0:
        MOTOR1.motors[0].power = BIAS00 * DCONST * speed
        MOTOR1.motors[1].power = BIAS01 * DCONST * speed
        MOTOR2.motors[0].power = BIAS10 * DCONST * speed
        MOTOR2.motors[1].power = BIAS11 * DCONST * speed
    else:
        MOTOR1.motors[0].power = -BIAS00 * DCONST * speed
        MOTOR1.motors[1].power = -BIAS01 * DCONST * speed
        MOTOR2.motors[0].power = -BIAS10 * DCONST * speed
        MOTOR2.motors[1].power = -BIAS11 * DCONST * speed
    
    r.sleep((abs(distance) * DTIME)/speed)

    MOTOR1.motors[0].power = 0
    MOTOR1.motors[1].power = 0
    MOTOR2.motors[0].power = 0
    MOTOR2.motors[1].power = 0

    r.sleep(rest)

def turn(angle: float, unit: str = 'd', speed: float = 0.2, rest: float = 0.1) -> None:
    '''
    One of two basic movemement functions.
    \nMakes the robot rotate through an angle (mostly) on the spot.
    \nThe angle unit defaults to d for degrees but can be changed to r for radians
    \nThe speed defaults to 0.2 and controls what fraction of maximum power is used
    '''

    if unit == 'r':
        angle = degrees(angle)
    elif unit != 'd':
        raise ValueError(f'This is not an acceptable angle unit')
    
    if angle >= 0:
        MOTOR1.motors[0].power = BIAS00 * ACONST * speed
        MOTOR1.motors[1].power = BIAS01 * ACONST * speed
        MOTOR2.motors[0].power = -BIAS10 * ACONST * speed
        MOTOR2.motors[1].power = -BIAS11 * ACONST * speed
    else:
        MOTOR1.motors[0].power = -BIAS00 * ACONST * speed
        MOTOR1.motors[1].power = -BIAS01 * ACONST * speed
        MOTOR2.motors[0].power = BIAS10 * ACONST * speed
        MOTOR2.motors[1].power = BIAS11 * ACONST * speed

    r.sleep((angle * ATIME)/speed)

    MOTOR1.motors[0].power = 0
    MOTOR1.motors[1].power = 0
    MOTOR2.motors[0].power = 0
    MOTOR2.motors[1].power = 0

    r.sleep(rest)

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
    robot.sleep(6)
    servoBoard.servos[PINIONSERVO].position = 0

def arm_move(new_pos: float) -> NotImplementedError:
    '''
    Moves the arm to a different height.
    \nnew_pos is a decimal between 0 and 1 which is how far up the pinion to go
    \nThis is unfortunately no longer just a wrapper since we now have to come up with logic for this
    \nOne of the things left to do. Not yet implemented
    '''
    
    distance = arm_height - new_pos
    #Run the servo for a certain amount of time
    arm_height = new_pos

    raise NotImplementedError('The arm functions have not yet been made')

def grab() -> NotImplementedError:
    '''
    Closes the arm if it is not already closed.
    \nNot yet implemented
    '''

    if arm_open:
        pass #Close
        arm_open = False
    
    raise NotImplementedError('The arm functions have not yet been made')

def release() -> NotImplementedError:
    '''
    Opens the arm if it is not already open.
    \nNot yet implemented
    '''

    if not arm_open:
        pass #Open
        arm_open = True
    
    raise NotImplementedError('The arm functions have not yet been made')

def align(marker_ID, accuracy: float = 0.02, type: str = 'h') -> None:
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

def drive_towards(marker_ID, dist_from: float = 3, precision: float = 0.01) -> None:
    '''
    Drives the robot towards a marker and stops
    dist_from away.
    \ndist_from defaults to 5.

    \nKenny: I'm looking at this again at 1am on the day of the competition and it is really horrible code.
    However, I am a few hours past having the presence of mind to fix it, so it will have to do.
    I don't even remember what all the arbitrary values are for.
    If something breaks, please don't ask me what went wrong
    '''

    try:
        stop = False
        align(marker_ID, 0.02, 'h')
        r.sleep(0.1)
        dist_remain = get_distance(marker_ID)

        dis = ((dist_remain - dist_from)/1500) - 3
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
        drive_towards(marker_ID, dist_from, precision)  #We love potentially infinite loops due to bad practice

def go_to_pick(marker_ID, s_height: float = 0, e_height: float = 1, a_height: float = 0) -> None:
    '''
    Moves the robot to the marker and picks it up. 
    s_height and e_height are passed to the pickup function
    as start_height and end_height respectively. a_height is the approach height
    '''

    arm_move(a_height)
    drive_towards(marker_ID, 3, precision=0.005)
    pickup(start_height=s_height, end_height = e_height)

def escape() -> None:
    '''
    Pretty self-explanatory.
    \nChecks available directions and moves in one of them
    \nKenny: I believe this is the last function I made for the Virtual League.
    This would explain both why it appears in all the try/excepts and why it is called escape.
    It was also the only function in this file without a docstring, which I guess makes sense
    '''
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
        print('trapped') #Kind of surprised this never showed up in the actual Virtual League

def search_any(type: str = 'Any', wanted_ID: int = None, floor: bool = False):
    '''Return a list of markers. 
    \nIf none are seen, turns until at least one is spotted. 
    \nIf a full 360 turn has been completed, returns an empty list.
    \nIf wanted_ID is given, looks for that specific ID.
    \nIf type is given, only considers markers of that type
    \nKenny: This and the align function required no edits. This is the only one I feel confident about, though.
    Hopefully that means the functions are getting abstract enough not to require much change.
    The time is 1:26 am, time for logic'''

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
