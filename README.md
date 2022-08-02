# SGAI - DRHAT - Outbreak
This is the repository that Beaverworks' SGAI 2022 will be using to understand
serious games and reinforcement learning.

## Team Courtney I - DR. HAT!
The best team out there.

## How to run
### VS Code version
DO NOT run main.py when the current directory is SGAI-Outbreak.
You must open the folder SGAI_MK3 with vscode. Then, you can
run main.py from VS Code.
### cmd line version
First, `cd ./SGAI_MK3`. Then, `python main.py`
### PyCharm version
Download the zip file and open SGAI-DRHAT-Outbreak. Ensure that numpy and pygame are installed, then run main.py.

## How to play
This game implements a KILL/CURE option, where you choose if you want to kill a zombie or cure it. 
Pay attention to the public outrage and public anxiety, as if they get too high, you lose. 
There are basic moves:
- Move - click on a person that you control and a square next to them.
If the square isn't occupied, the person will move to that square.
- Bite - If you are playing as a zombie, 
you can click the bite button and a zombie and then a person.
to turn the person into a zombie. 
- Heal - If you are playing as the government, you 
can click the cure button and a person (the healer) and then a zombie (the healee).
There is 50% chance that the zombie will be healed and become a person again 
(this is curing). If the zombie is not healed, the healer may become a zombie.
If they are healed, they now have 100% immunity to being zombified. 
- Kill - If you are playing as the government, you can click the kill button and a person (the killer) and then a zombie (the victim).
Killing ensures that the zombie goes away with no chance of infection, however, it spikes the public's outrage, so choose carefully.
- Vaccinate - In order to vaccinate a human, you must move into a "safe space". Safe spaces are slate blue on the board. Clicking on the red plus symbol will vaccinate everyone in a safe space. There can be up to two safe spaces, and up to one person in each safe space. 

