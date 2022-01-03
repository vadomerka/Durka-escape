import os
import sys
import random
import pygame


all_sprites = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
cells_group = pygame.sprite.Group()
creatures_group = pygame.sprite.Group()
cell_w = cell_h = 50
gravity = 0.16
width = 1000
height = 800


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


class Weapon(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.equipped = False
        self.speed_x = 0
        self.speed_y = 0
        self.count = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.anim_on = False

    def update(self):
        self.count += 1
        if self.count == 10:
            self.image = pygame.transform.scale(load_image('spoon.png'), (cell_w, cell_h))
            self.anim_on = False
        if pygame.sprite.collide_mask(self, player):
            self.equipped = True
        if self.equipped and not self.anim_on:
            self.rect.y = player.rect.y
            self.rect.x = player.rect.x - 20
        elif self.equipped and self.anim_on:
            self.rect.x = player.rect.x - 30
            self.rect.y = player.rect.y + 30
        else:
            self.speed_y += gravity
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            if self.rect.x >= (width - player_w):
                self.speed_x = -self.speed_x
            elif self.rect.x <= 0:
                self.speed_x = -self.speed_x
            if self.rect.y >= (height - player_h // 2):
                self.rect.y = (height - player_h // 2)
            elif self.rect.y <= 0:
                self.rect.y = 0

    def shoot(self):
        self.image = pygame.transform.scale(load_image('hit_spoon.png'), (player_w, player_h // 2))
        self.anim_on = True
        self.count = 0


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
        if self.health <= 0:
            self.kill()
        if self.move_down:
            self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.collide_walls(width, 0, 0, height)
        if pygame.sprite.spritecollideany(self, walls_group):
            for wall in walls_group:
                if pygame.sprite.collide_rect(self, wall):
                    self.collide_walls(wall.rect.x, (wall.rect.x + wall.rect.width),
                                       wall.rect.y, (wall.rect.y + wall.rect.height))

    def collide_walls(self, left_x, right_x, up_x, down_x):
        if self.rect.x >= (left_x - self.rect.width):
            self.move_right = False
            self.rect.x = left_x - self.rect.width
        elif not pygame.sprite.spritecollideany(self, walls_group):
            self.move_right = True
        if self.rect.x <= right_x:
            self.move_left = False
            self.rect.x = right_x
        elif not pygame.sprite.spritecollideany(self, walls_group):
            self.move_left = True

        if self.rect.y >= (down_x - self.rect.height):
            self.move_down = False
            self.rect.y = (down_x - self.rect.height)
            self.move_up = True
        else:
            self.move_down = True
        if self.rect.y <= up_x:
            self.rect.y = up_x
            self.move_up = False


class Enemy(Creature):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(img, pos_x, pos_y, cell_w, cell_h)

    def update(self):
        super().update()
        if pygame.sprite.collide_mask(self, self.player):
            self.speed_x = 0
            self.player.health -= 0.5


class Player(Creature):
    def __init__(self, img, pos_x, pos_y, player_w, player_h):
        super().__init__(img, pos_x, pos_y, player_w, player_h, health=100, damage=0, speed=5)
        self.image = pygame.transform.scale(img, (player_w, player_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
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
    def __init__(self, cell_size=50, win_width=1000, win_height=800):
        global width, height, cell_w, cell_h, gravity
        self.cell_h = self.cell_w = cell_w = cell_h = cell_size
        gravity = 0.1
        self.window_size = width, height = win_width, win_height
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

        self.start_screen()

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
            # self.screen.fill((0, 0, 0))  # здесь должна быть заставка
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            all_sprites.draw(self.screen)
            all_sprites.update()
            self.clock.tick(self.fps)
            pygame.display.flip()
        self.level(stage=self.stage)

    def level(self, stage):
        x, y = self.generate_level(self.load_level("level " + str(stage)))
        self.player = Player(self.player_img, x, y, self.player_w, self.player_h)
        for creature in creatures_group:
            creature.player = self.player
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.movement("y", "up")
            if keys[pygame.K_LEFT]:
                self.player.movement("x", "left")
                # player.direction = 1
                # player.flip()
            if keys[pygame.K_RIGHT]:
                # player.flip()
                # player.direction = 0
                self.player.movement("x", "right")
            if keys[pygame.K_DOWN]:
                pass
                # player.movement("y", "down")
            if keys[pygame.K_SPACE]:
                # print(1)
                pass
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # если юзер не двигается по х, тогда стоп
                self.player.movement("x", "stop")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN:
                    pass
                elif event.type == pygame.KEYUP and last_event[pygame.K_SPACE]:
                    gun.shoot()
                elif event.type == pygame.K_SPACE:
                    print(1)
                # if random.random() > 0.5:
                #     enemy.movement("x", "right")
                # else:
                #     enemy.movement("x", "left")
            last_event = keys
            all_sprites.draw(self.screen)
            all_sprites.update()
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
        filename = file_path + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def generate_level(self, level):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Cell(self.empty_cell, x, y)
                elif level[y][x] == '#':
                    Wall(self.wall_cell, x, y)
                elif level[y][x] == '@':
                    Cell(self.empty_cell, x, y)
                    new_player = x, y
                elif level[y][x] == 'X':
                    Cell(self.empty_cell, x, y)
                    Enemy(self.enemy_img, x, y)
        return new_player


# player = Player(5, 5, player_img)
# dragon = AnimatedSprite(load_image("dragon_sheet8x2.png"), 8, 2, 50, 50)
# gun = Weapon(7, 8, gun_img)
# enemy = Enemy(7, 7, enemy_img)
# # bullet = Bullet(bul_img)


def main():
    Game(cell_size=50, win_width=1000, win_height=1000)


main()

"""running = True
        while running:
            screen.fill((0, 0, 0))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player.movement("y", "up")
            if keys[pygame.K_LEFT]:
                player.movement("x", "left")
                # player.direction = 1
                # player.flip()
            if keys[pygame.K_RIGHT]:
                # player.flip()
                # player.direction = 0
                player.movement("x", "right")
            if keys[pygame.K_DOWN]:
                pass
                # player.movement("y", "down")
            if keys[pygame.K_SPACE]:
                # print(1)
                pass
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # если юзер не двигается по х, тогда стоп
                player.movement("x", "stop")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    pass
                elif event.type == pygame.KEYUP and last_event[pygame.K_SPACE]:
                    gun.shoot()
                elif event.type == pygame.K_SPACE:
                    print(1)
                if random.random() > 0.5:
                    enemy.movement("x", "right")
                else:
                    enemy.movement("x", "left")
            last_event = keys
            all_sprites.draw(screen)
            all_sprites.update()
            clock.tick(fps)
            pygame.display.flip()"""
