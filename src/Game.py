import math
from math import cos, sin, atan

import pygame as pg
from random import randint

# frame rate per second
from pygame.math import Vector2

FPS = 60

# window screen size
WSIZE = (720, 480)
screen = pg.display.set_mode(WSIZE)

# size of tile
TSIDE = 32
TSIZE = TSIDE, TSIDE

cell_img = pg.Surface(TSIZE)


def rect_vertexes(rect):
    if rect.w > TSIDE or rect.h > TSIDE:
        vertexes = [(rect.right - 1, rect.top), (
            rect.right - 1, rect.bottom - 1)]
        x, y = rect.topleft
        for i in range(0, rect.w - 1, TSIDE - 1):
            for j in range(0, rect.h - 1, TSIDE - 1):
                vertexes.append((x + i, y + j))
        for i in range(0, rect.w - 1, TSIDE - 1):
            vertexes.append((x + i, rect.bottom - 1))
        for j in range(0, rect.h - 1, TSIDE - 1):
            vertexes.append((rect.right - 1, y + j))
    else:
        vertexes = [rect.topleft, (rect.left, rect.bottom - 1), (rect.right - 1, rect.top), (
            rect.right - 1, rect.bottom - 1)]
    return vertexes


class Player:
    size = (16, 16)
    # 0 - arrows; 1 - with rotate, 2 - with rotate mouse
    type_movement = 2

    def __init__(self, position, game_map):
        self.rect = pg.Rect(position, self.size)
        self.game_map = game_map
        self.speed = 0.2
        self.rot_speed = 0.005
        self.rotation = 0
        self.screen_position = (-1, -1)

    def set_screen_position(self, position):
        self.screen_position = position

    def pg_event(self, event):
        pass

    def update(self, tick=20):
        keys = pg.key.get_pressed()
        movement = [0, 0]
        speed = self.speed * tick
        if self.type_movement == 0:
            if keys[pg.K_LEFT]:
                movement[0] -= speed
            elif keys[pg.K_RIGHT]:
                movement[0] += speed
            if keys[pg.K_UP]:
                movement[1] -= speed
            elif keys[pg.K_DOWN]:
                movement[1] += speed

            if movement[0] and movement[1]:
                at = atan(movement[1] / movement[0])
                movement = movement[0] * abs(sin(at)), movement[1] * abs(cos(at))
        elif self.type_movement in {1, 2}:
            if self.type_movement == 1:
                rot_speed = self.rot_speed * tick
                if keys[pg.K_RIGHT]:
                    self.rotation -= rot_speed
                elif keys[pg.K_LEFT]:
                    self.rotation += rot_speed
            elif self.type_movement == 2:
                self.rotation = -Vector2((0, 0)).angle_to(Vector2(pg.mouse.get_pos()) - Vector2(self.screen_position))\
                                / 180 * math.pi + math.pi / 2
            if keys[pg.K_UP]:
                movement = Vector2(math.sin(self.rotation), math.cos(self.rotation)) * speed
            elif keys[pg.K_DOWN]:
                movement = Vector2(-math.sin(self.rotation), -math.cos(self.rotation)) * speed
        self.move(movement)

    def move(self, movement):
        self.rect.x += movement[0]
        for collision in self.game_map.rect_collision(self.rect):
            if movement[0] > 0:
                self.rect.right = collision[0] * TSIDE
            elif movement[0] < 0:
                self.rect.left = collision[0] * TSIDE + TSIDE
        self.rect.y += movement[1]
        for collision in self.game_map.rect_collision(self.rect):
            if movement[1] > 0:
                self.rect.bottom = collision[1] * TSIDE
            elif movement[1] < 0:
                self.rect.top = collision[1] * TSIDE + TSIDE


class GameMap:
    default = 0

    def __init__(self, size, ):
        self.size = size
        self.array_map = self.set_map_of_sym(self.default)

    def pg_event(self, event):
        pass

    def get_tile(self, position):
        return self.array_map[position[1]][position[0]]

    def get_tile_with_def(self, position, default=None):
        if 0 <= position[0] < self.size[0] and 0 <= position[1] < self.size[1]:
            return self.get_tile(position)
        return default

    def load(self, text: str):
        arr2d = [list(map(int, st)) for st in text.split("\n") if st]
        self.size = (len(arr2d[0]), len(arr2d))
        self.array_map = arr2d

    def set_map_of_sym(self, sym=0):
        self.array_map = [[sym for i in range(self.size[0])] for j in range(self.size[1])]
        return self.array_map

    def random_set(self, points=10):
        for i in range(points):
            x, y = randint(0, self.size[0] - 1), randint(0, self.size[1] - 1)
            self.array_map[y][x] = 1

    def rect_collision(self, rect: pg.Rect):
        collisions = []
        for x, y in rect_vertexes(rect):
            if self.get_tile_with_def((x // TSIDE, y // TSIDE)):
                collisions.append((x // TSIDE, y // TSIDE))
        return collisions


class Game:
    def __init__(self):
        self.screen = screen
        self.game_map = GameMap((10, 10))
        self.game_map.random_set(10)
        self.player = Player((0, 0), self.game_map)
        self.camera = Camera(self)
        self.clock = pg.time.Clock()
        self.running = True

    def pg_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit()
            self.player.pg_event(event)
            self.game_map.pg_event(event)

    def main(self):
        self.running = True
        while self.running:
            tick = self.clock.tick(FPS)
            pg.display.set_caption(f"FPS: {self.clock.get_fps()}")
            self.pg_events()
            self.player.update(tick)
            self.camera.draw(self.screen)
            pg.display.flip()

    def exit(self):
        self.running = False


class Camera:
    def __init__(self, game: Game):
        self.game_map = game.game_map
        self.player = game.player
        self.rect = pg.Rect((0, 0), WSIZE)
        self.move_to_player()
        self.display = pg.Surface(WSIZE)

    def move_to_player(self):
        self.rect.x = self.player.rect.x - WSIZE[0] // 2
        self.rect.y = self.player.rect.y - WSIZE[1] // 2

    def draw(self, surface):
        self.display.fill("white")
        self.rect.x += (self.player.rect.x - self.rect.x - WSIZE[0] // 2) / 5
        self.rect.y += (self.player.rect.y - self.rect.y - WSIZE[1] // 2) / 5
        for iy in range(self.game_map.size[1]):
            for ix in range(self.game_map.size[0]):
                t = self.game_map.get_tile((ix, iy))
                if t == 1:
                    tx, ty = ix * TSIDE - self.rect.x, iy * TSIDE - self.rect.y
                    self.display.blit(cell_img, (tx, ty))
        pg.draw.rect(self.display, "black", (-self.rect.x, -self.rect.y,
                                             self.game_map.size[0] * TSIDE, self.game_map.size[1] * TSIDE),
                     1)
        self.draw_player()
        surface.blit(self.display, (0, 0))

    def draw_player(self):
        px, py = self.player.rect.centerx - self.rect.x, self.player.rect.centery - self.rect.y
        self.player.set_screen_position((px, py))
        pos_2 = px + math.sin(self.player.rotation) * 12, \
                py + math.cos(self.player.rotation) * 12
        pg.draw.circle(self.display, "green", (px, py), self.player.rect.w // 2)
        pg.draw.line(self.display, "red", (px, py), pos_2, 1)


def main():
    return Game().main()
