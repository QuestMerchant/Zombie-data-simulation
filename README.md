# Zombie Outbreak
### Video Demo: [URL](https://youtu.be/gyWyb_pgk_Y)
### Description:
This a visual represntation of possible outcome should a single zombie enter a crowd. The user can set how densely populated the area is to see how it affects the chances of survival.
I chose matplotlib to show the visual representation as I only needed some basic plotting to be shown and it didn't require interactivity apart from population density.
I chose to use numpy as well, as it improves speed and memory management when array sizes are static and I have a 2-d array with the same number of columns to gain benefit of numpy.


#### Conditions:
- Patient zero roams mindlessly, unless an uninfected is within range.
- Uninfected must not attack immediately until the situation is known, but they may defend themselves
- Zombies have a slightly faster movement
- Increase speed when fleeing or attacking
- Group majority vote to decide whether to leave uninfected alone or kill them
- 80% of population set to flee instead of fighting
- Always a chance of being infected during encounters
- Fighters increase chance of surviving encounter once alert of situation

#### Challenges faced:
I went through many methods and test on how to effectively make uninfected move across the graph randomly without changing direction all the time as the zombies do.
There were many methods to determine distances of zombies and uninfected, and I had to try find calculations that worked well enough but weren't terribly inefficient. Unfortunately I couldn't find a way to get a radius arounf the current position and view all the points within that radius. Also sometimes with some functionality, such as getting the distance of nearby, I had to run the calculations again despite knowing which were nearby because I didn't have the original index. I could keep the original index to avoid that, however that would've required getting the distance from every state on every loop which would be less efficient. I was unable to determine whether calculating the distance of the few nearby was more or less efficient than scanning through the originally calculated distances array and picking all the ones that met the criteria.
My code had become quite messy near the end and I had to go back and see that smaller functions could be made to make the code neater and easier to read.

#### Results:
It appears as though in a very low populated area, too many are infected by the time peole take action. In a moderately populated area, survivibility is highest. In very densely populated situations, infection rates are very high and there is no chance of surviving.
