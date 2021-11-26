import pygame
import math


def draw_triAngle(sc, ang, r):
    color = pygame.Color("white")
    deg = math.radians(ang - 15)
    x1 = math.cos(deg) * r + 100
    y1 = math.sin(deg) * r + 100
    deg = math.radians(ang + 15)
    x2 = math.cos(deg) * r + 100
    y2 = math.sin(deg) * r + 100
    pygame.draw.polygon(sc, color, [(100, 100), (x1, y1), (x2, y2)], width=0)


def draw_vent(sc, angle):
    # if angle < 0:
    #     angle += 360*10
    color = pygame.Color("white")
    pygame.draw.circle(sc, color, (100, 100), 10)

    draw_triAngle(sc, angle + 30, 70)
    draw_triAngle(sc, angle + 150, 70)
    draw_triAngle(sc, angle + 270, 70)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 201, 201
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    a = 0
    speed = 0
    draw_vent(screen, a)
    count = 0
    clock = pygame.time.Clock()
    fps = 60
    mouse_pos = None
    move = False
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    speed += 5
                if event.button == 3:
                    speed -= 5
        a += speed
        draw_vent(screen, a)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
