import os
import sys
import random
import pygame


all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
cells_group = pygame.sprite.Group()
creatures_group = pygame.sprite.Group()
entities_group = pygame.sprite.Group()
weapons_group = pygame.sprite.Group()
cell_w = cell_h = 50
gravity = 0.16
win_w = 500
win_h = 500
pl_x = 0
pl_y = 0
level = None
level_width = 1000
level_height = 800


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites, creatures_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.count = 0
        self.pos = (500, 500)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        # self.pos =
        # self.rect.x, self.rect.y = player.rect.x, player.rect.y
        if self.count % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.count += 1


class Cell(pygame.sprite.Sprite):
    def __init__(self, cell_image, pos_x, pos_y):
        super().__init__(cells_group, all_sprites)
        self.image = pygame.transform.scale(cell_image, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, cell_image, pos_x, pos_y):
        super().__init__(cells_group, all_sprites, walls_group)
        self.image = pygame.transform.scale(cell_image, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        if obj is not Player:
            obj.rect.x += self.dx
            obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        # if win_w // 2 <= target.rect.x <=
        self.dx = -(target.rect.x + target.rect.w // 2 - win_w // 2)
        # print(target.rect.x + target.rect.w // 2)
        # print(target.rect.y)
        if (target.rect.y + target.rect.h) <= (win_h // 2):
            self.dy = -(target.rect.y + target.rect.h // 2 - win_h // 2)
        else:
            self.dy = 0


class Entity(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y, groups=(all_sprites, entities_group)):
        super().__init__(groups)
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = random.randint(-5, 5)
        self.speed_y = random.randint(-3, 0)

    def update(self):
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.collide_walls(level_width, 0, 0, level_height)

    def collide_walls(self, left_x, right_x, up_x, down_x):
        if self.rect.x >= (left_x - self.rect.width):
            self.speed_x = 0
            self.rect.x = left_x - self.rect.width
        if self.rect.x <= right_x:
            self.speed_x = 0
            self.rect.x = right_x

        if self.rect.y >= (down_x - self.rect.height):
            self.speed_y = 0
            self.speed_x = 0
            self.rect.y = (down_x - self.rect.height)
        if self.rect.y <= up_x:
            self.rect.y = up_x
            self.speed_y = 0


class Weapon(Entity):
    def __init__(self, *entity_args):
        super().__init__(*entity_args, groups=(all_sprites, entities_group, weapons_group))

    def update(self):
        super().update()

    def shoot(self):
        self.image = pygame.transform.scale(load_image('hit_spoon.png'), (player_w, player_h // 2))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__(all_sprites)
        pass
        # self.image = pygame.transform.scale(img, (player_w, player_h))
        # self.rect = self.image.get_rect().move(
        #    cell_w * pos_x, cell_h * pos_y)
        # self.speed_x = 0
        # self.speed_y = 0
        # self.pos = (pos_x, pos_y)
        # self.mask = pygame.mask.from_surface(self.image)


class Creature(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y, self_width, self_height, health=100, damage=5, speed=2):
        super().__init__(all_sprites, creatures_group)
        self.image = pygame.transform.scale(img, (self_width, self_height))
        self.rect = self.image.get_rect().move(cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.player = None
        self.health = health
        self.damage = damage
        self.movement_speed = speed
        self.move_down = True
        self.move_left = True
        self.move_right = True
        self.move_up = True
        # self.mask = pygame.mask.from_surface(self.image)

    def movement(self, line, direction="up"):
        if line == "x":
            if direction == "right" and self.move_right:
                vx = self.movement_speed
            elif direction == "left" and self.move_left:
                vx = -self.movement_speed
            elif direction == "stop":
                vx = 0
            else:
                vx = 0
                # print("wrong direction", line)
            self.speed_x = vx
        if line == "y":
            if direction == "down" and self.move_down:
                vy = 0
            elif direction == "up":
                if self.move_up:
                    vy = -self.movement_speed
                    self.move_up = False
                else:
                    vy = self.speed_y
            else:
                vy = 0
                print("wrong direction", line)
            self.speed_y = vy
        if line == "stop":
            pass

    def update(self):
        self.collide()
        if self.rect.y == self.min_y:
            self.plat = True
            self.speed_y -= gravity
        else:
            self.plat = False
        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.x >= self.max_x:
            self.rect.x = self.max_x
        if self.rect.x <= self.min_x:
            self.rect.x = self.min_x

        if self.rect.y >= self.min_y:
            self.rect.y = self.min_y
        if self.rect.y <= self.max_y:
            self.rect.y = self.max_y

    def collide(self):
        global gravity
        row = self.rect.y // cell_h + self.rect.h // cell_h
        col = (self.rect.x + 5) // cell_w
        if 0 <= row < level_height // cell_h and 0 <= col < level_width // cell_h:
            if level[row][col] == '#' or \
                    level[self.rect.y // cell_h + self.rect.h // cell_h][(self.rect.x + cell_w - 5) // cell_w] == '#':
                self.min_y = (self.rect.y // cell_h) * cell_h
            else:
                self.min_y = level_height - self.rect.height

            if level[self.rect.y // cell_h][(self.rect.x + 5) // cell_w] == '#' or \
                    level[self.rect.y // cell_h][(self.rect.x + cell_w - 5) // cell_w] == '#':
                self.max_y = self.rect.y // cell_h * cell_h
                self.speed_y = 0
                self.rect.y = self.max_y + cell_h
            else:
                self.max_y = 0

            if level[self.rect.y // cell_w][self.rect.x // cell_w + self.rect.w // cell_w] == '#' or \
                    level[self.rect.y // cell_w + 1][self.rect.x // cell_w + self.rect.w // cell_w] == '#':
                self.max_x = self.rect.x
            else:
                self.max_x = level_width - self.rect.w

            if level[self.rect.y // cell_h][self.rect.x // cell_w] == '#' or \
                    level[self.rect.y // cell_h + 1][self.rect.x // cell_w] == '#':
                self.min_x = self.rect.x
                self.rect.x += 1
            else:
                self.min_x = 0

        # if level[player.rect.y // 100][round(player.rect.x * 2 / 100)] == '#':
        #     self.min_y = player.rect.y - 100

class Enemy(Creature):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(img, pos_x, pos_y, cell_w, cell_h)

    def update(self):
        super().update()
        if pygame.sprite.collide_mask(self, self.player):
            self.speed_x = 0
            self.player.health -= 1


class Player(Creature):
    def __init__(self, img, pos_x, pos_y, player_w, player_h):
        super().__init__(img, pos_x, pos_y, player_w, player_h, health=100, damage=0, speed=5)
        self.image = pygame.transform.scale(img, (player_w, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        # self.level_x = pos_x * cell_w
        # self.level_y = pos_y * cell_h
        self.speed_x = 0
        self.speed_y = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0

    def flip(self):
        if self.direction == 0 or 1:
            self.image = pygame.transform.flip(self.image, flip_y=False, flip_x=True)
            self.direction = 2


class Game:
    def __init__(self, cell_size=50, win_width=500, win_height=500):
        global level_width, level_height, cell_w, cell_h, gravity, win_w, win_h
        self.cell_h = self.cell_w = cell_w = cell_h = cell_size
        gravity = 0.1
        self.window_size = win_w, win_h = win_width, win_height
        self.player = None
        self.player_h = self.cell_h * 2
        self.player_w = self.cell_w
        self.stage = 1

        pygame.init()
        pygame.display.set_caption("Durka")
        self.screen = pygame.display.set_mode(self.window_size)
        self.screen.fill(pygame.Color("black"))

        self.clock = pygame.time.Clock()
        self.fps = 60

        self.player_img = self.load_image('sad_cat.jpg')
        self.enemy_img = self.load_image('box.png')
        self.gun_img = self.load_image('spoon.png')
        self.bul_img = self.load_image('hit.png')
        self.empty_cell = self.load_image("yellow wall.jpg")
        self.wall_cell = self.load_image("mood.jpg")
        self.heart_image = pygame.transform.scale(self.load_image("heart.png"), (cell_w, cell_h))

        self.start_screen()
        self.level(stage=self.stage)

    def start_screen(self):
        intro_text = ["ЗАСТАВКА", "",
                      "Правила игры кто прочитал, тот сдохнет",
                      "",
                      ""]

        fon = pygame.transform.scale(self.load_image('sad_cat.jpg'), self.window_size)
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            all_sprites.draw(self.screen)
            all_sprites.update()
            self.clock.tick(self.fps)
            pygame.display.flip()

    def draw_interface(self):
        for hp in range(0, self.player.health, 5):
            self.screen.blit(self.heart_image, (hp * 10, 0))

    def level(self, stage):
        self.load_level(stage)
        self.generate_level()
        # camera = Camera()

        running = True
        while running:
            self.screen.fill((0, 0, 0))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.movement("y", "up")
            if keys[pygame.K_LEFT]:
                self.player.movement("x", "left")
            if keys[pygame.K_RIGHT]:
                self.player.movement("x", "right")
            if keys[pygame.K_SPACE]:
                pass
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # если юзер не двигается по х, тогда стоп
                self.player.movement("x", "stop")
            last_event = keys
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    pass
                elif event.type == pygame.KEYUP and last_event[pygame.K_SPACE]:
                    gun.shoot()
                elif event.type == pygame.K_SPACE:
                    print(1)
            # camera.update(self.player)
            # обновляем положение всех спрайтов
            # for sprite in all_sprites:
            #     camera.apply(sprite)
            all_sprites.draw(self.screen)
            all_sprites.update()
            self.draw_interface()
            self.clock.tick(self.fps)
            pygame.display.flip()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def load_image(self, name, colorkey=None, file_for_images="data"):
        fullname = os.path.join(file_for_images, name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image

    def load_level(self, filename, file_path="data/levels/"):
        global level_width, level_height, level
        filename = file_path + "level " + str(filename)
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(map(len, level_map))
        level_map = list(map(lambda x: x.ljust(max_width, '.'), level_map))
        level_height = len(level_map) * cell_h
        level_width = len(level_map[0]) * cell_w
        level = level_map

    def generate_level(self):
        global pl_x, pl_y, level
        playerxy, enemies, entities = None, [], []
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Cell(self.empty_cell, x, y)
                elif level[y][x] == '#':
                    Wall(self.wall_cell, x, y)
                elif level[y][x] == '@':
                    Cell(self.empty_cell, x, y)
                    playerxy = x, y
                elif level[y][x] == 'X':
                    Cell(self.empty_cell, x, y)
                    enemies.append((Enemy, self.enemy_img, x, y))
                elif level[y][x] == 'W':
                    Cell(self.empty_cell, x, y)
                    entities.append((Weapon, self.gun_img, x, y))
        pl_x, pl_y = playerxy[0] * cell_w, playerxy[1] * cell_h
        for clas, img, x, y in enemies:
            clas(img, x, y)
        for clas, img, x, y in entities:
            clas(img, x, y)
        x, y = playerxy
        self.player = Player(self.player_img, x, y, self.player_w, self.player_h)
        for creature in creatures_group:
            creature.player = self.player


def main():
    Game(cell_size=50, win_width=1000, win_height=1000)


main()
