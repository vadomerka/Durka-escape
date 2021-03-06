import os
import sys
import random
import pygame


cell_h = cell_w = 50
size = width, height = 1000, 800
player_h = cell_h * 2
player_w = cell_w
gravity = 0.1
creature_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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


def load_level(filename):
    filename = "data/levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))
    # print(list(map(lambda x: list(x.ljust(max_width, '.')), level_map)))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(lev):
    new_player, x, y = None, None, None
    obj = []
    for y in range(len(lev)):
        print(lev[y])
        for x in range(len(lev[y])):
            if lev[y][x] == '.':
                wall = Wall('empty', x, y)
                walls.append(wall)
            if lev[y][x] == '#':
                wall = Wall('wall', x, y)
                walls.append(wall)
            if lev[y][x] == '@':
                wall = Wall('empty', x, y)
                walls.append(wall)
                new_player = x, y
                lev[y][x] = "."
            if lev[y][x] == 'X':
                wall = Wall('empty', x, y)
                walls.append(wall)
                obj.append((Enemy, x, y, enemy_img))
            if lev[y][x] == 'W':
                wall = Wall('empty', x, y)
                walls.append(wall)
                obj.append((Gun, x, y, gun_img))
                lev[y][x] = "."
    for clas, x, y, img in obj:
        clas(x, y, img)
    new_player = Player(new_player[0], new_player[1], player_img)
    return new_player, lev


def draw_interface():
    for hp in range(0, player.health, 5):
        screen.blit(heart_image, (hp * 5, 0))


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, ev):
        for sprite in self:
            sprite.get_event(ev)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, ev):
        pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y, group):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos_x, pos_y)
        self.count = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if self.count % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.count += 1


class Gun(Sprite):
    def __init__(self, pos_x, pos_y, img):
        global player_group
        super().__init__(player_group)
        self.type = "spoon"
        self.damage = 5
        self.attack_speed = 1
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.move_speed = 2
        self.speed_x = random.randint(-self.move_speed, self.move_speed)
        self.speed_y = random.randint(-self.move_speed, 0)
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.plat = False
        self.near_player = False
        self.min_y = height - self.rect.h
        self.max_y = 0
        self.max_x = width - self.rect.w
        self.min_x = 0

        self.equipped = False

    def update(self):
        self.collide()
        if self.rect.y == self.min_y:
            self.plat = True
            self.speed_y -= gravity
        else:
            self.plat = False
        if self.plat:
            self.speed_x = 0
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

        if pygame.sprite.collide_mask(self, player):
            self.draw_stats()
            # self.equip()
            self.near_player = True
        else:
            self.near_player = False

    def draw_stats(self):
        last_stats = [0, 0]
        intro_text = ["Wanna grab a " + self.type + " ?",
                      "             old stats: damage, " + str(last_stats[0]) + " speed, " + str(last_stats[1]),
                      "             new stats: damage, " + str(self.damage) + " speed, " + str(self.attack_speed)]

        fon = pygame.transform.scale(gun_img, (width * 0.8, height * 0.8))
        screen.blit(fon, (width * 0.1, height * 0.1))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        # pygame.display.flip()

    def equip(self):
        player.weapon = self
        player_group.remove(self)

    def collide(self):
        row1 = self.rect.y // cell_h + self.rect.h // cell_h
        row2 = self.rect.y // cell_h + self.rect.h // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.min_y = (self.rect.y // cell_h) * cell_h
        else:
            self.min_y = height - self.rect.height
        row1 = self.rect.y // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        row2 = self.rect.y // cell_h
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.max_y = self.rect.y // cell_h * cell_h
            self.speed_y = 0
            self.rect.y = self.max_y + cell_h
        else:
            self.max_y = 0
        row1 = self.rect.y // cell_w
        col1 = self.rect.x // cell_w + self.rect.w // cell_w
        row2 = self.rect.y // cell_w + 1
        col2 = self.rect.x // cell_w + self.rect.w // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.max_x = self.rect.x
        else:
            self.max_x = width - player_w
        row1 = self.rect.y // cell_h
        col1 = self.rect.x // cell_w
        row2 = self.rect.y // cell_h + 1
        col2 = self.rect.x // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.min_x = self.rect.x
            self.rect.x += 1
        else:
            self.min_x = 0

    def shoot(self):
        print("bang")


class Bullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__(all_sprites)
        pass


class Wall(Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(all_sprites)
        self.name = img
        img = tile_images[img]
        self.image = pygame.transform.scale(img, (cell_w, cell_h))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 0

    def update(self):
        if pygame.sprite.collide_mask(self, player):
            pass


class Creature(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img, size_x, size_y, health=100, damage=1, speed=2):
        super().__init__(all_sprites, creature_group)
        self.image = pygame.transform.scale(img, (size_x, size_y))
        self.rect = self.image.get_rect().move(
            cell_w * pos_x, cell_h * pos_y)
        self.speed_x = 0
        self.speed_y = 0
        self.health = health
        self.damage = damage
        self.move_speed = speed
        self.pos = (pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.plat = False
        self.min_y = height - self.rect.height
        self.max_y = 0
        self.max_x = width - self.rect.width
        self.min_x = 0

    def movement(self, line, direction="up"):
        if line == "x":
            if direction == "right":
                vx = self.move_speed
            elif direction == "left":
                vx = -self.move_speed
            elif direction == "stop":
                vx = 0
            else:
                vx = 0
                print("wrong direction", line)
            self.speed_x = vx
        if line == "y":
            if direction == "down":
                vy = 0
            elif direction == "up":
                if self.rect.y == self.min_y or self.plat:
                    vy = -self.move_speed
                else:
                    vy = self.speed_y
            else:
                vy = 0
                print("wrong direction", line)
            self.speed_y = vy
        if line == "stop":
            pass

    def update(self):
        # умирание
        if self.health <= 0:
            self.kill()

        # коллайд со стенами
        self.collide()
        # елси на платформе
        if self.rect.y == self.min_y:
            self.plat = True
            self.speed_y -= gravity
        else:
            self.plat = False

        self.speed_y += gravity
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # функция стен (!ее нельзя переносить относительно других штук в этой функции!)
        if self.rect.x >= self.max_x:
            self.rect.x = self.max_x
        if self.rect.x <= self.min_x:
            self.rect.x = self.min_x

        if self.rect.y >= self.min_y:
            self.rect.y = self.min_y
        if self.rect.y <= self.max_y:
            self.rect.y = self.max_y

    def collide(self):
        row1 = self.rect.y // cell_h + self.rect.h // cell_h
        row2 = self.rect.y // cell_h + self.rect.h // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.min_y = (self.rect.y // cell_h) * cell_h
        else:
            self.min_y = height - self.rect.height
        row1 = self.rect.y // cell_h
        col1 = (self.rect.x + self.move_speed) // cell_w
        row2 = self.rect.y // cell_h
        col2 = (self.rect.x + cell_w - self.move_speed) // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.max_y = self.rect.y // cell_h * cell_h
            self.speed_y = 0
            self.rect.y = self.max_y + cell_h
        else:
            self.max_y = 0
        row1 = self.rect.y // cell_w
        col1 = self.rect.x // cell_w + self.rect.w // cell_w
        row2 = self.rect.y // cell_w + 1
        col2 = self.rect.x // cell_w + self.rect.w // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.max_x = self.rect.x
        else:
            self.max_x = width - player_w
        row1 = self.rect.y // cell_h
        col1 = self.rect.x // cell_w
        row2 = self.rect.y // cell_h + 1
        col2 = self.rect.x // cell_w
        if 0 <= row1 < len(level) and 0 <= col1 < len(level[-1]) and \
                0 <= row2 < len(level) and 0 <= col2 < len(level[-1]) and \
                level[row1][col1] == '#' or \
                level[row2][col2] == '#':
            self.min_x = self.rect.x
            self.rect.x += 1
        else:
            self.min_x = 0


class Enemy(Creature):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(pos_x, pos_y, img, cell_w, cell_h * 2)

    def movement(self, line, direction="up"):
        if line == "x":
            vx = 0
            if direction == "right":
                vx = self.move_speed
            elif direction == "left":
                vx = -self.move_speed
            elif direction == "stop":
                vx = 0
            self.speed_x = vx

    def AI(self):
        direction = random.randint(0, 3)
        if direction <= 1:
            self.movement("x", "left")
        elif direction <= 2:
            self.movement("x", "stop")
        else:
            self.movement("x", "right")

    def update(self):
        super().update()
        self.AI()
        if pygame.sprite.collide_mask(self, player):
            player.health -= self.damage


class Player(Creature):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(pos_x, pos_y, img, cell_w, cell_h * 2, damage=0, speed=5)
        self.weapon = None

    # def update(self):
        # super().update()

    def attack(self):
        self.weapon.shoot()


if __name__ == '__main__':
    cell_h = cell_w = 50
    size = width, height = 1000, 800
    player_h = cell_h * 2
    player_w = cell_w
    gravity = 0.1

    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()

    pygame.init()
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    player_img = load_image('mar.png')
    enemy_img = load_image('box.png')
    gun_img = load_image('spoon.png')
    bul_img = load_image('hit.png')
    wall_img = load_image('box.png')
    heart_image = load_image("small_heart.png")
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }

    all_sprites = SpriteGroup()
    player_group = SpriteGroup()
    walls = []
    level_map = load_level('room 0')

    player, level = generate_level(level_map)
    # gun = Gun(7, 10, gun_img)
    # enemy = Enemy(4, 7, enemy_img)

    running = True
    while running:
        screen.fill((0, 0, 0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.movement("y", "up")
        if keys[pygame.K_a]:
            player.movement("x", "left")
        if keys[pygame.K_d]:
            player.movement("x", "right")
        if keys[pygame.K_s]:
            player.movement("y", "down")
        # if keys[pygame.K_SPACE]:
            # print(player.rect.y // 100 + 1, round(player.rect.x * 2 / 100 print()+ 1))
        if not (keys[pygame.K_a] or keys[pygame.K_d]):  # если юзер не двигается по х, тогда стоп
            player.movement("x", "stop")

        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # нужно будет заменить ноль на константу из pygame (девая кнопка мыши)
            player.attack()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if pygame.sprite.spritecollideany(player, player_group):
                        # берем все предметы, и оставляем только те, с которыми коллайдится игрок
                        equipable_entities = list(filter(
                            lambda obj: pygame.sprite.collide_mask(player, obj), list(player_group)))
                        equipable_entities[-1].equip()
                pass

        all_sprites.draw(screen)
        player_group.draw(screen)
        all_sprites.update()
        player_group.update()
        draw_interface()
        clock.tick(fps)
        pygame.display.flip()
