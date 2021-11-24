import pygame


def ger_size(it):
    try:
        if len(it) != 2:
            raise Exception
        s = list(map(int, it))
        # if s[0] % s[1] != 0:
        #     raise Exception
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
    # pygame.draw.rect(screen, pygame.Color("black"), left_down, width=0)


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


if __name__ == '__main__':
    pygame.init()
    intput = input().split()
    while ger_size(intput) is None:
        print("Неправильный формат ввода")
        intput = input().split()
    w_len, num = ger_size(intput)
    size = width, height = w_len * num * 2, w_len * num * 2
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("миша")

    draw_mish(screen, size, w_len, num)
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pygame.display.flip()
        pass
    pygame.quit()
