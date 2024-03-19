Car-bumping game made to test different reinforcement learning algorithms and to introduce me to curiosity-driven learning as well as compare it to older algorithms ad models.

# The Game
The basic physics that the game uses were coded from scratch by me (because I like physics)
The Game rules as follow:
* There are a number of cars on screen (30-50)
* The bumper of each car is strong
* The sides and back of each car are weak
* Each car gets points by bumping into other cars' weak parts with its bumper
* Cars can use a turbo to propel themselves forward very fast but it is limited ad has a cooldown period
* (Might be added) There can be items on the 'arena' that cars can pick up and shoot forward 
* The items can slow dow other cars or cause them to lose steering...

# The "Brain"
The reinforcement learning algorithms are to be programmed from scratch in Python. I will focus on Gentic algorithms and curosity-driven leaning.

I prefer coding the RL algorithms from scratch to familiarize myself with the basics and the logic as well as to have full control and ability to tweak any aspect of the algorithms once they are running.
Multiple models are to be used to control the cars, both against cars from the same model and later against other models in the same arena. This will show how models learn when learning against the same model Vs how models learn against each other.

I will code measures to prevent any one model from going extinct when other models make a jump in learning. The measures will be for example ensuring there are at least three cars of each model at any generation in the arena.

My hypothesis is that, once the models learn in arenas specified for each model, learning together will both show the strongest model as well as help all models learn better by diversifying the competition and preventing models to learn how to counter one specific style.
