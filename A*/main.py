from gui import *
import os,sys
import pygame as pg 
from queue import PriorityQueue

W,H = 600,700
os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
screen = pg.display.set_mode((W,H))
pg.display.set_caption('A*')
clock = pg.time.Clock()
reset = Button('Reset', (50,650),color='black',size=18)
start = Button('Start', (200,650),color='black',size=18)
rows_input = Input(['Rows', '25'], (300, 650),4, size=15)
class Node():
	def __init__(self, row, col, size, total_rows):
		self.row = row
		self.col = col
		self.x = row*size
		self.y = col*size
		self.color = (255,255,255)
		self.w , self.h = size, size
		self.total_row = total_rows
		self.neighbors = []
		self.work = True
		self.size = 0
	def make_open(self):
		self.color = (153,216,230)
	def make_closed(self):
		self.color = (225,225,213)
	def make_path(self):
		self.color = (255,255,0)
	def make_end(self):
		self.color = (0,255,0)
	def get_pos(self):
		return self.row, self.col
	def is_barrier(self):
		return self.color == (0,0,0)
	def reset(self):
		self.color = (255,255,255)
	def draw(self):
		if self.color != (255,255,255):
			if self.size < self.w/2:
				self.size += 0.2
				pg.draw.circle(screen, self.color, (self.x+self.w/2, self.y+self.h/2),self.size)
			else:
				pg.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
		else:
			pg.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
	def update(self, grid):
		self.neighbors = []
		if self.row < self.total_row - 1 and not grid[self.row+1][self.col].is_barrier(): #down
			self.neighbors.append(grid[self.row+1][self.col])

		if self.row > 0 and not grid[self.row-1][self.col].is_barrier(): #up
			self.neighbors.append(grid[self.row-1][self.col])

		if self.col < self.total_row - 1 and not grid[self.row][self.col+1].is_barrier(): #right
			self.neighbors.append(grid[self.row][self.col+1])

		if self.col > 0 and not grid[self.row][self.col-1].is_barrier(): #left
			self.neighbors.append(grid[self.row][self.col-1])

	def __lt__(self, other):
		return False

class Algorithm():
	def __init__(self):
		self.count = 0
		self.open_set = PriorityQueue()
		self.came_from = {}
		self.g_score = 0
		self.end = None
		self.draw = None
		self.start = None
		self.stop =False
	def find_path(self, came_from, current, draw):
		for i in range(1000000):
			if current in came_from:
				current = came_from[current]
				current.make_path()
				draw()
			else:
				break
	def make_new(self, draw,grid,start,end):
		self.count = 0
		self.open_set = PriorityQueue()
		self.open_set.put((0, self.count, start))
		self.came_from = {}
		self.g_score = {node:float('inf') for row in grid for node in row}
		self.g_score[start] = 0
		self.f_score = {node:float('inf') for row in grid for node in row}
		self.f_score[start] = self.h(start.get_pos(), end.get_pos())
		self.open_set_hash = {start}
		self.start = start
		self.draw = draw
		self.end = end
		self.stop = False
	def update(self):
		if not self.open_set.empty() and not self.stop:
			current = self.open_set.get()[2]
			self.open_set_hash.remove(current)
			if current == self.end:
				self.find_path(self.came_from,self.end, self.draw )
				self.end.make_end()
				self.start.make_end()
				self.stop = True
				return True
			for neighbor in current.neighbors:
				temp_g_score = self.g_score[current] + 1
				if temp_g_score < self.g_score[neighbor]:
					self.came_from[neighbor] = current
					self.g_score[neighbor] = temp_g_score
					self.f_score[neighbor] = temp_g_score + self.h(neighbor.get_pos(), self.end.get_pos())
					if neighbor not in self.open_set_hash:
						self.count += 1
						self.open_set.put((self.f_score[neighbor], self.count, neighbor))
						self.open_set_hash.add(neighbor)
						neighbor.make_open()
			self.draw()
			if current != self.start:
				current.make_closed()
		return False
	def h(self, p1, p2):
		return abs(p1[0]-p2[0]) + abs(p1[1]- p2[1])

class Game():
	def __init__(self):
		self.rows = 25
		self.start = None 
		self.end = None
		self.started = False
		self.alg = Algorithm()
	def draw_grid(self):
		gap = W//self.rows
		for i in range(self.rows):
			pg.draw.line(screen, (150,150,150), (0,i*gap), (H, i*gap))
			for i in range(self.rows):
				pg.draw.line(screen, (150,150,150), (i*gap,0), (i*gap,W))
	def make_grid(self):
		grid = []
		gap = W// self.rows
		for row in range(self.rows):
			grid.append([])
			for col in range(self.rows):
				grid[row].append(Node(row,col, gap, self.rows))
		return grid
	def get_mouse(self):
		gap = W//self.rows
		x,y = pg.mouse.get_pos()
		row = x//gap
		col = y//gap
		return row, col
	def create(self, grid):
		if pg.mouse.get_pressed()[0]:
			row, col = self.get_mouse()
			try:
				node = grid[row][col]
				if not self.start and node !=self.end:
					self.start = node
					self.start.color = (255,0,0)
				elif not self.end and node != self.start:
					self.end = node
					self.end.color = (0,0,255)
				elif node != self.end and node != self.start:
					node.color = (0,0,0)
			except:
				pass
	def destroy(self,grid):
		if pg.mouse.get_pressed()[2]:
			row, col = self.get_mouse()
			node = grid[row][col]
			if node == self.start:
				self.start = None
			elif node == self.end:
				self.end = None
			node.reset()
	def update(self):
		grid = self.make_grid()
		while 1:
			clock.tick(60)
			event =  pg.event.get()
			for i in event:
				if i.type == pg.QUIT:
					pg.quit()
					sys.exit()
			if self.started:
				if self.alg.update():
					self.started = False
			self.create(grid)
			self.destroy(grid)	
			self.draw(grid)
			if reset.draw(screen):
				grid = self.make_grid()
				self.start = None
				self.end = None
				self.started = False
			if not self.started:
				if start.draw(screen):
					self.started = True
					for row in grid:
						for node in row:
							node.update(grid)
					self.alg.make_new(lambda: self.draw(grid), grid, self.start, self.end)
			rows_input.draw(screen, event)
			if self.start == None:
				self.rows = rows_input.choice()
				if self.rows == None:
					self.rows = 25
				if type(self.rows) == str:
					self.rows = int(self.rows)
			Label(screen, 'By: Kostia :)', (450, 650), size=18)
			pg.display.update()
	def draw(self, grid):
		screen.fill((255,255,255))
		for row in grid:
			for node in row:
				node.draw()
		self.draw_grid()

			



main = Game()
main.update()