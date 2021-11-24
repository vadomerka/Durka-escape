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


def draw_chess(screen, s, cell):
    
    first_color = pygame.Color("black")
    if (s % cell) % 2 == 0:
        first_color = pygame.Color("white")

    for row in range(0, s, cell):
        for col in range(0, s, cell):
            coords = row, col, cell, cell
            pygame.draw.rect(screen, first_color, coords, width=0)
            if first_color == pygame.Color("black"):
                first_color = pygame.Color("white")
            else:
                first_color = pygame.Color("black")
    # pygame.draw.rect(screen, pygame.Color("black"), left_down, width=0)


def draw_tic(screen, w, h):
    screen.fill((0, 0, 0))
    color = pygame.Color("white")
    pygame.draw.line(screen, color, (0, 0), (w, h), width=10)
    pygame.draw.line(screen, color, (0, h), (w, 0), width=10)


def draw_red(scree, w, h):
    screen.fill((0, 0, 0))
    pygame.draw.rect(scree, (255, 0, 0), (1, 1, w - 2, h - 2), width=0)


if __name__ == '__main__':
    pygame.init()
    intput = input().split()
    while ger_size(intput) is None:
        print("Неправильный формат ввода")
        intput = input().split()
    # intput = ger_size(intput)
    size = width, height = ger_size(intput)
    # cell = intput[1]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Rect")

    draw_red(screen, width, height)
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pygame.display.flip()
        pass
    pygame.quit()
