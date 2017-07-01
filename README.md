# Robocup project
## Introduction:
We want to find 2 different object and then let both object in different target position.
For example, we will have a ball and a Lego construction in the class. The robot has to find the first object, go there, catch it, go to the target position where we want to drop the object and after that do the same but with the second object.
## Steps:
- The robot has to search for the first object around the class. If the robot doesn’t find the object at the beginning position, the robot should move a bit and check for it at the new position. If after, 3-4 movement without finding the object, the robot stops the execution of the programm saying “ I can’t find it”. For this step we need:
  - The robot has to rotate around himself 360 º to search for the object. The robot rotates in small angle step
  - To detect the object we need maschine learning. We need to find different object.
- When we know where is the object with maschine learning, we can know the position of it and how far away we are. We can move the robot until we are really close to it (it doesn’t matter if we see the object with the camera or not at the end, because we know it is there)
- When we are really close and in front of it, we want to turn our robot. We want to catch the ball from the side(maybe with the right hand). 
- When we catch it, we have to search for the object’s target position. The same than before(Maschine learning to find it, calculate the distance and walk there)
- When we are there, drop the object and repite the steps to search for the second object.
