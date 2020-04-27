# Copyright 2020 Ethan Tillison

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import time

username = "etillison3350"

directions = (("left", -1, 0), ("right", 1, 0), ("up", 0, -1), ("down", 0, 1))

if __name__ == "__main__":
	os.system("echo Running gitland bot. Press ^C to stop.")
	
	work_dir = os.path.abspath(".")
	server_dir = os.path.abspath("./gitland")
	
	player_dir = os.path.join(server_dir, "players", username)
	
	last_direction = "right"
	
	while True:
		os.chdir(server_dir)
		os.system("git pull origin master")
		
		with open(os.path.join(player_dir, "team"), 'r') as teamfile:
			team = teamfile.read()[1]
		
		with open(os.path.join(player_dir, "x"), 'r') as xfile:
			x = int(xfile.read())
			
		with open(os.path.join(player_dir, "y"), 'r') as yfile:
			y = int(yfile.read())
			
		with open(os.path.join(server_dir, "map"), 'r') as mapfile:
			map = [row.split(",") for row in mapfile.read().split()]
		
		valid_directions = [(dir, dx, dy, map[y + dy][x + dx][1]) for dir, dx, dy in directions
				if x + dx >= 0 and x + dx < len(map[y]) and y + dy >= 0 and y + dy < len(map)
				and map[y + dy][x + dx][0] == 'u']
				
		if len(valid_directions) == 0:
			direction = "right"
		else:
			useful_directions = [dir for dir, dx, dy, color in valid_directions
					if color != team]
			if len(useful_directions) > 0:
				if last_direction in useful_directions:
					direction = last_direction
				else:
					direction = useful_directions[0]
			else:
				valid_directions = [dir for dir, dx, dy, color in valid_directions]
				if last_direction in valid_directions:
					direction = last_direction
				else:
					direction = valid_directions[0]
		
		with open(os.path.join(work_dir, "act"), 'w') as actfile:
			actfile.write(direction)
		last_direction = direction
		
		os.chdir(work_dir)
		os.system("git add act")
		os.system("git commit -m \"Next turn\"")
		os.system("git push origin master")
		
		time.sleep(1)
		
		os.system("echo Moving " + last_direction)
		
		time.sleep(59)
