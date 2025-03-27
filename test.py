from sr.robot3 import *
robot = Robot()
this_ard = robot.arduino
this_ard.pins[10].mode = OUPUT
print('OUTPUT')
for letter in ['c', 'b', 's']:
  this_ard.command(letter)
  print(letter)
  robot.sleep(2)
