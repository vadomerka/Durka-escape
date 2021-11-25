import pygame


def ger_size(it):
    try:
        if len(it) != 2:
            raise Exception
        s = list(map(int, it))
        if s[0] % 4 != 0 or not (0 <= s[1] <= 360) or not (0 <= s[0] <= 100):
            raise Exception
        return s
    except Exception:
        return None


def draw_chess(screen, s, c):
    color = pygame.Color("black")
    if c % 2 == 0:
        color = pygame.Color("white")
    cell_size = s[0] // c
    for row in range(0, s[0], cell_size):
        for col in range(0, s[0], cell_size):
            coords = row, col, cell_size, cell_size
            pygame.draw.rect(screen, color, coords, width=0)
            # pygame.display.flip()
            if color == pygame.Color("black"):
                color = pygame.Color("white")
            else:
                color = pygame.Color("black")
        if c % 2 == 0:
            if color == pygame.Color("black"):
                color = pygame.Color("white")
            else:
                color = pygame.Color("black")
    # pygame.draw.rect(screen, pygame.Color("black"), left_down, width=0) \


def draw_tic(screen, w, h):
    screen.fill((0, 0, 0))
    color = pygame.Color("white")
    pygame.draw.line(screen, color, (0, 0), (w, h), width=10)
    pygame.draw.line(screen, color, (0, h), (w, 0), width=10)


def draw_red(scree, w, h):
    screen.fill((0, 0, 0))
    pygame.draw.rect(scree, (255, 0, 0), (1, 1, w - 2, h - 2), width=0)


def draw_mish(scree, s, w, n):
    scree.fill((0, 0, 0))
    color = pygame.Color("red")
    center = s[0] // 2, s[0] // 2
    for i in range(1, n + 1):
        rad = i * w
        pygame.draw.circle(scree, color, center, rad, width=w)
        # pygame.display.flip()
        if i % 3 == 1:
            color = pygame.Color("green")
        elif i % 3 == 2:
            color = pygame.Color("blue")
        else:
            color = pygame.Color("red")


def draw_sphere(scree, s, n):
    scree.fill((0, 0, 0))
    color = pygame.Color("white")
    for i in range(0, n):
        # pygame.draw.ellipse
        pygame.draw.ellipse(scree, color, (0, (i * (150 // n)), 300, 300 - i * (300 // n)), width=1)
        pygame.display.flip()
    for i in range(0, n):
        # pygame.draw.ellipse
        pygame.draw.ellipse(scree, color, (i * (150 // n), 0, 300 - i * (300 // n), 300), width=1)
        pygame.display.flip()


def draw_blocks(scree, s):
    scree.fill(pygame.Color("white"))
    color = pygame.Color("red")
    for row in range(0, 200, 17):
        start = 0
        if row // 17 % 2 != 0:
            start = -16
        for col in range(start, 300, 32):
            pygame.draw.rect(scree, color, (col, row, 30, 15), width=0)


def draw_block(scree, a, colour):
    scree.fill(pygame.Color("black"))
    color = pygame.Color("red")
    hsv = color.hsva
    color.hsva = (colour, hsv[1], 75, hsv[3])
    pygame.draw.rect(scree, color, (100, 175, a, a), width=0)
    color.hsva = (colour, hsv[1], 100, hsv[3])
    pygame.draw.polygon(scree, color,
                        [[100, 175], [100 + a // 2, 175 - a // 2],
                         [100 + a + a // 2, 175 - a // 2], [100 + a, 175]])
    color.hsva = (colour, hsv[1], 50, hsv[3])
    pygame.draw.polygon(scree, color,
                        [[100 + a, 175], [100 + a + a // 2, 175 - a // 2],
                         [100 + a + a // 2, 175 + a // 2], [100 + a, 175 + a]])


if __name__ == '__main__':
    pygame.init()
    intput = input().split()
    while ger_size(intput) is None:
        print("Неправильный формат ввода")
        intput = input().split()
    intput = ger_size(intput)
    size = width, height = 300, 300
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("кирпичи")

    draw_block(screen, intput[0], intput[1])
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pygame.display.flip()
        pass
    pygame.quit()
