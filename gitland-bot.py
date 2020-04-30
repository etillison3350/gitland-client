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
import subprocess
import time
from math import floor

username = "etillison3350"

directions = {(-1, 0): "left", (1, 0): "right", (0, -1): "up", (0, 1): "down"}
colors = {
		"r": ["""\033[31m""", """\033[31m""", """\033[91m"""],
		"g": ["""\033[32m""", """\033[32m""", """\033[92m"""],
		"b": ["""\033[34m""", """\033[34m""", """\033[94m"""],
		"x": ["""\033[37m"""]
}

max_decay = 0
planned_steps = 9

def adj(x, y, m):
	a = []
	if x > 0:
		a.append((x - 1, y))
	if y > 0:
		a.append((x, y - 1))
	if (x < len(m[y]) - 1):
		a.append((x + 1, y))
	if (y < len(m) - 1):
		a.append((x, y + 1))
	return a

# def getcost(x, y, m, d, c):
#	return max_decay + (max_decay - d[y][x]) * (1 if m[y][x][1] == c else 0 if m[y][x][1] == 'x' else -1)

# Cost function for Dijkstra's. The following are in cost-order (lowest to highest)
#  - Cells that have been captured recently by another color
#  - Unclaimed cells
#  - Cells of our color that will be lost soon
def getcost(x, y, tilecolor, tiledecay, c):
	return max_decay + tiledecay * (1 if tilecolor == c else 0 if tilecolor == 'x' else -1)

if __name__ == "__main__":
	os.system("color")
	os.system("echo Running gitland bot. Press ^C to stop.")
	
	work_dir = os.path.abspath(".")
	server_dir = os.path.abspath("./gitland")
	
	player_dir = os.path.join(server_dir, "players", username)
	
	last_direction = "right"
	
	while True:
		os.chdir(server_dir)
		os.system("git pull origin master")
				
		with open(os.path.join(server_dir, "map"), 'r') as mapfile:
			map = [row.split(",") for row in mapfile.read().split()]
			
		with open(os.path.join(server_dir, "decay"), 'r') as decayfile:
			decay = decayfile.read().split()
		for y in range(len(decay)):
			row = []
			for x in decay[y].split(','):
				d = int(x)
				if d > max_decay:
					max_decay = d
				row.append(d)
			decay[y] = row
		
		with open(os.path.join(player_dir, "team"), 'r') as teamfile:
			team = teamfile.read()[1]
			
		with open(os.path.join(player_dir, "timestamp"), 'r') as timefile:
			timestamp = float(timefile.read())
		
		with open(os.path.join(player_dir, "y"), 'r') as yfile:
			ay = int(yfile.read())
		
		with open(os.path.join(player_dir, "x"), 'r') as xfile:
			ax = int(xfile.read())
		
		# Dijkstra's algorithm, looking for the best path of length exactly planned_steps
		explored = {(ax, ay): (None, 0, 0)}
		work = {(ax, ay)}
		while len(work):
			x, y = min(work, key=lambda n: explored[n][1])
			work.remove((x, y))
			_, cost, dist = explored[(x, y)]
			if dist < planned_steps:
				for nx, ny in adj(x, y, map):
					if map[ny][nx][0] == 'u':
						ncost = cost + getcost(nx, ny, map[ny][nx][1], max(0, decay[ny][nx], dist + 1), team)
						if (nx, ny) in explored:
							_, ecost, _ = explored[(nx, ny)]
							if ncost < ecost:
								explored[(nx, ny)] = ((x, y), ecost, dist + 1)
								work.add((nx, ny))
						else:
							explored[(nx, ny)] = ((x, y), ncost, dist + 1)
							work.add((nx, ny))
		target = min([k + v for k, v in explored.items() if v[2] == planned_steps], default=None, key=lambda i: i[3])
		if target == None:
			direction = "idle"
		else:
			path = []
			pos = target[0:2]
			while pos != None:
				path.insert(0, pos)
				pos = explored[pos][0]
			direction = directions[(path[1][0] - path[0][0], path[1][1] - path[0][1])]
		
		with open(os.path.join(work_dir, "act"), 'w') as actfile:
			actfile.write(direction)
		
		os.chdir(work_dir)
		os.system("git add act")
		os.system("git commit -m \"Next turn\"")
		os.system("git push origin master")
		
		time.sleep(1)
		
		os.system("echo --------------------");
		
		os.system("echo At ({}, {}), Moving {}".format(ax, ay, direction))
		
		os.system("echo Maximum decay value is assumed to be {}".format(max_decay));
		
		os.system("echo Current board:")
		
		for py in range(len(map)):
			row = map[py]
			echo = ""
			for px in range(len(row)):
				color = row[px][1]
				if color in colors.keys():
					if px == ax and py == ay:
						symbol = "(#)"
					elif (px, py) in path:
						symbol = ":{}:".format(floor(10 * decay[py][px] / (max_decay + 1)))
					elif row[px][0] == 'u':
						symbol = "[{}]".format(floor(10 * decay[py][px] / (max_decay + 1)))
					else:
						symbol = "(@)"
					
					shades = colors[color]
					color = shades[floor(decay[py][px] / ((max_decay + 1) / len(shades)))]
					echo += color + symbol
				else:
					echo += """\033[0m[-]"""
			subprocess.call(["echo", "-e", echo + """\033[0m"""], shell = False)
		
		t = time.time() - timestamp
		subprocess.call(["echo", "Last update: {:.2f}s ago".format(t)]);
		t = 120 - t
		if (t < 10):
			t = 60
		subprocess.call(["echo", "Next update in {:.2f}s".format(t)]);
		time.sleep(t)
