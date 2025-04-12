'''
This is where the high level logic takes place.
Imports from the movement library and is imported 
by the robot.py file.

Must run init_Zone() before anything else to automatically set the zone
'''

from movement import *


def game() -> None:
    '''
    The master gameplay loop.
    It is the only thing called in robot.py
    It can be considered the strategy function
    '''
     #Hope this works
    tick = 1
    timer_start = r.time()
    current = r.time()
    #I might change this loop tomrrow - oh wait I mean today
    #I did in fact change the loop but it is still not very good
    #It is 3am and I need to sleep
    while (current - timer_start) < 60:
        if tick % 3 == 0:
            get_points(1)
        else:
            get_points(0)
        current = r.time()
        tick += 1
    
    while True:
        big_attempt()
    

def init_Zone() -> None:
    '''
    This function is deprecated and was only for the Virtual League. Please access the Robot.zone attribute directly
    \nInitialises myZone by seeing which high rise is in front of the robot.
    \nKenny: I'm really mad about this. I felt so smart when I realised I could do this and now they just give it to us.
    '''
    
    global myZone

    if (closest(dest=False).id) == 195:
        myZone = 'z0'
    elif (closest(dest=False).id) == 196:
        myZone = 'z1'
    elif (closest(dest=False).id) == 197:
        myZone = 'z2'
    else:
        myZone = 'z3'

def closest(type: str = 'Any', dest: bool = True, pallet: bool = False, floor: bool = True, zoned = True):
    '''
    Returns the closest marker. If type is given,
    only considers a specific category of markers. 
    \nIf dest is true, only considers pallets that can be stacked upon
    \nIf pallet is True, only considers pallets
    \nFloor is passed to the search_any function, so does the same thing as in that
    \nzoned is whether the marker is in the vicinity of a high rise
    '''

    marks = search_any(type, floor = floor)
    try:
        if dest:
            marks = [mark for mark in marks if valid_place(mark)]

        if pallet:
            marks = [mark for mark in marks if (id_type(mark.id) in range(1, 5))]
        
        if not zoned:
            marks = [mark for mark in marks if not is_zoned(mark)]
        
        return marks[0]
    except:
        escape()
        return closest(type=type, dest=dest, pallet=pallet, floor=floor)

def is_zoned(mark) -> bool:
    high_rises = get_markers(type = 'mid rise') + get_markers(type = 'high rise')

    for rise in high_rises:
        hoz_tolerance = 0.18
        dist_tolerance = 200
        
        angles = (mark.position.horizontal_angle, rise.position.horizontal_angle)
        distances = (mark.position.distance, rise.position.distance)
        
        if ((max(angles) - min(angles)) < hoz_tolerance) and ((max(distances) - min(distances)) < dist_tolerance):
            return True
    
    return False


def deposit(dest: (str | int) = 'cen', dist_from = 1) -> None:
    '''
    Goes to dest and releases the pallet.
    If dest is given as an int, goes to that ID marker.
    If dest is given as a string, goes to the closest 
    marker of that category. dest defaults to cen (centre)
    '''
    

    if type(dest) == int:
        drive_towards(dest, dist_from, 0.02)
        tower_height = [((max_height(tower(dest)) // 100)), 0]

    elif dest == 'mid':
        id = closest('mid rise', floor = False).id
        maximal = max_height(tower(id))
        tower_height = [((maximal// 100)), 0]
        drive_towards(id, dist_from, 0.02)
        
    elif dest == 'cen':
        drive_towards(199, dist_from, 0.01)
        tower_height = [1, -1]
    elif dest == 'back':
        drive_towards('back', dist_from, 0.05)
    else:
        print('not an option')
        return
    
    arm_move(max(tower_height))
    r.sleep(0.1)
    drop()
    drive(-1)

def pallet_place(dest: (str | int) = 'mid', a_height = 0, dist_from = 1) -> None:
    '''
    The complete pallet placing function.
    \ndest defaults to mid (mid high rise) but can be set to either an integer marker id or a string marker type.
    \na_height is the approach height and dist_from is the distance from the target that the robot stops at
    '''
    target = closest(myZone, floor = True, zoned = False)
    if target != None:
        go_to_pick(target.id, a_height=a_height)
        deposit(dest, dist_from)
    else:
        print('Not seen')


#New stuff from 2am
 
def get_points(mode: int = 0) -> None:
    '''
    The different actions we can take.
    \nMode is an integer that refers to one of the strategies:
    \n0 is normal mode, 1 is frantic mode
    '''
    match mode:
        case 0:
            normal_mode()
        case 1:
            big_attempt()
        case 2:
            hoard()


def normal_mode() -> None:
    our_pallets = search_any(type = MEANS[r.zone+1][3])
    
    for pallet in our_pallets:
        if max_height(tower(pallet.id)) >= 100:
            if valid_place(pallet):
                pallet_place(pallet.id)
            else:
                pallet_place(pallet.id, dist_from=155)
            return
    
    pallet_place()

def big_attempt() -> None:
    pallet_place('cen')

def hoard() -> NotImplementedError:
    '''
    This is an experimental feature that has not yet been implemented.
    There should be no way to reach this, but please do not attempt to use it
    '''
    raise NotImplementedError

    #pallet_place('back')