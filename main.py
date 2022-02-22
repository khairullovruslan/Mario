import pygame
import os
import sys
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()
size = WIDTH, HEIGHT = 550, 550
screen = pygame.display.set_mode(size)
FPS = 50
STEP = 6


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=-1):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
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

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_groups[tile_type], all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, *args, **kwargs) -> None:
        x, y = 0, 0
        if pygame.key.get_pressed()[K_LEFT]:
            x -= tile_width * STEP // FPS
        if pygame.key.get_pressed()[K_RIGHT]:
            x += tile_width * STEP / FPS
        if pygame.key.get_pressed()[K_UP]:
            y -= tile_width * STEP / FPS
        if pygame.key.get_pressed()[K_DOWN]:
            y += tile_width * STEP / FPS
        self.rect = self.rect.move(x, y)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-x, -y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
         self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
         self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


if __name__ == '__main__':
    camera = Camera()
    start_screen()
    # создадим группу, содержащую все спрайты
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mar.png')

    tile_width = tile_height = 50

    all_sprites = pygame.sprite.Group()
    # группы спрайтов

    player_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    empty_group = pygame.sprite.Group()

    tile_groups = {
        'wall': walls_group,
        'empty': empty_group
    }
    try:

        player, level_x, level_y = generate_level(load_level(input()))

    except Exception as e:
        print(e)
        terminate()
    running = True
    pygame.display.set_caption('Desantura')
    clock = pygame.time.Clock()

    while running:
        screen.fill('black')
        # if pygame.mouse.get_focused():
        #     screen.blit(image, pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_LEFT:
        #             player.rect.x -= STEP
        #         if event.key == pygame.K_RIGHT:
        #             player.rect.x += STEP
        #         #if event.key == pygame.K_DOWN:
        #         #    player.rect.y += STEP
        #         #if event.key == pygame.K_UP:
        #             player.rect.y -= STEP
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     Landing(event.pos)
        # if event.type == pygame.MOUSEMOTION:
        #     if pygame.mouse.get_focused():
        #         screen.blit(image, event.pos)

        tick = clock.tick()
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
             camera.apply(sprite)

        all_sprites.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        all_sprites.update()
        clock.tick(FPS)
    terminate()