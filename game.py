from pygame import *
import pygame

# Instruction:
# ESC -- выход в главное меню
# SPACE -- перезапустить уровень
# F -- стрельба
# arrows LEFT, RIGHT, UP -- перемещение влево, вправо и наверх соответственно

init()
# Параметры окна
WIDTH = 800
HEIGHT = 600

mixer.music.load('fon_music.mp3')
mixer.music.play(-1)

b_ground = transform.scale(image.load('sprites/background.png'), (800, 600))

shot = transform.scale(image.load("sprites/shot_pixian_ai.png"), (167, 80))

# Определение спрайтов для анимации
frames_right = [
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((0, 0), (190, 200))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((194, 0), (150, 209))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((335, 0), (102, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((440, 0), (122, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((570, 0), (172, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((745, 0), (180, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((928, 0), (151, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((1068, 0), (108, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((1175, 0), (128, 219))), (75, 85)),
    transform.scale(image.load("sprites/Hero.png").subsurface(Rect((1309, 0), (173, 219))), (75, 85))
]

frames_left = list()
for i in frames_right:
    frames_left.append(transform.flip(i, True, False))

player_icon_r = transform.scale(image.load("sprites/Hero.png").subsurface(Rect((0, 1015), (180, 230))), (75, 85))
player_icon_l = transform.flip(player_icon_r, True, False)


# Главный игрок
class Player(sprite.Sprite):
    right = True

    def __init__(self, shot):
        super().__init__()

        self.image = player_icon_r
        self.health = 3
        self.hearts_sprite_list = sprite.Group()
        for i in range(1, 4):
            self.hearts_sprite_list.add(Hearts(i * 70, 10))

        self.rect = self.image.get_rect()

        # Вектор скорости игрока
        self.vel_x = 0
        self.vel_y = 0

        self.shot = shot

    def update(self):
        flag_3 = False
        # Установка гравитации
        self.gravitation()
        x = self.vel_x
        # Передвигаем его на право/лево
        # vel_x будет меняться позже при нажатии на стрелочки клавиатуры
        if not (WIDTH // 2 - 150 < self.rect.x < WIDTH // 2 + 85):
            self.vel_x = 0
            if WIDTH // 2 - 150 < (self.rect.x + x) < WIDTH // 2 + 85:
                self.vel_x = x
        self.rect.x += self.vel_x
        # Проверка на столкновение
        block_hit_list = sprite.spritecollide(self, level_sprites, False)

        for block in block_hit_list:
            #  Не даём пройти сквозь предметы
            if isinstance(block, Platform):
                if self.vel_x > 0:
                    self.rect.right = block.rect.left
                    self.vel_x = 0
                elif self.vel_x < 0:
                    self.rect.left = block.rect.right
                    self.vel_x = 0
            elif isinstance(block, Bullet):
                self.health -= 1
                block.rect.x = -65
                for i in self.hearts_sprite_list:
                    self.hearts_sprite_list.remove(i)
                    break
            elif isinstance(block, Magma):
                self.health -= 1
                for i in self.hearts_sprite_list:
                    self.hearts_sprite_list.remove(i)
                break

        self.rect.y += self.vel_y

        # То же самое, только для вверх/вниз
        block_hit_list = sprite.spritecollide(self, level_sprites, False)
        # print(len(block_hit_list))
        for block in block_hit_list:
            if isinstance(block, Platform):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                # Останавливаем  движение
                self.vel_y = 0
            elif isinstance(block, Bullet):
                self.health -= 1
                block.rect.x = -68
                for i in self.hearts_sprite_list:
                    self.hearts_sprite_list.remove(i)
                    break
            elif isinstance(block, Magma):
                self.health -= 1
                if self.health <= 0:
                    return ''
            elif isinstance(block, CheckPoint):
                main_menu()

        if not (WIDTH // 2 - 150 < self.rect.x < WIDTH // 2 + 85):
            for j in level_sprites:
                j.rect.x += -x
                if ((self.rect.x < j.rect.x < self.rect.right) or (self.rect.x < j.rect.right < self.rect.right)) and (
                        self.rect.top < j.rect.y < self.rect.bottom):
                    if not isinstance(j, Canon) and not isinstance(j, Magma) and not isinstance(j, CheckPoint):
                        j.rect.x += x
                        flag_3 = True
                        break
                j.rect.x += x

            if not flag_3:
                for i in level_sprites:
                    i.rect.x += -x
                    self.rect.x += 0
        self.vel_x = x

    # В этой функции мы передвигаем игрока

    def gravitation(self):
        if self.vel_y == 0:
            self.vel_y = 1
        else:
            self.vel_y += 1

        if self.rect.y >= HEIGHT - self.rect.height and self.vel_y >= 0 and self.health > 0:
            self.vel_y = 0
            self.rect.y = HEIGHT - self.rect.height

    def move_left(self):
        self.vel_x = -9
        if self.right:
            self.flip()
            self.right = False

    def move_right(self):
        # то же самое, но вправо
        self.vel_x = 9
        if not self.right:
            self.flip()
            self.right = True

    # Передвижение игрока

    def jump(self):
        # Для этого опускаемся на 11 единиц, проверем соприкосновение и далее поднимаемся обратно
        self.rect.y += 11
        platform_hit_list = sprite.spritecollide(self, level_sprites, False)
        self.rect.y -= 11

        # Если все в порядке, прыгаем вверх
        if len(platform_hit_list) > 0 or self.rect.bottom >= HEIGHT:
            self.vel_y = -16

        # Стрельба

    def shoot(self):
        if self.image == player_icon_r or self.image in frames_right:
            self.shot.image = shot
            self.shot.rect.x = self.rect.x + 50
            self.shot.rect.y = self.rect.y
        else:
            self.shot.image = transform.flip(shot, True, False)
            self.shot.rect.x = self.rect.x - 140
            self.shot.rect.y = self.rect.y

        for i in sprite.spritecollide(self.shot, level_sprites, False):
            if isinstance(i, Canon):
                i.rect.y = 800
                for j in level_sprites:
                    if isinstance(j, Bullet):
                        j.rect.y = 800
            elif isinstance(i, Bullet):
                i.rect.x = -70

    def stop(self, icon):
        self.image = icon
        self.vel_x = 0

    def flip(self):
        # зеркальное отражение иконки
        self.image = transform.flip(self.image, True, False)


class Magma(sprite.Sprite):
    def __init__(self):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = image.load('sprites/magma.png')

        self.rect = self.image.get_rect()


# Класс для описания платформы
class Platform(sprite.Sprite):
    def __init__(self):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = image.load('sprites/platform.png')

        self.rect = self.image.get_rect()


class CheckPoint(sprite.Sprite):
    def __init__(self):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = transform.scale(image.load('sprites/ai_checkpoint2.png'), (100, 120))

        self.rect = self.image.get_rect()


# Создание и анимация снаряда
class Bullet(sprite.Sprite):
    def __init__(self, can, player):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = transform.scale(image.load('sprites/bullet.png'), (60, 50))
        self.pl = player
        self.canon = can
        self.rect = self.image.get_rect()
        self.vel = -5

    def update(self):
        self.rect.x += self.vel
        if abs(self.pl.rect.x - self.canon.rect.x) < 400:
            if self.rect.x < -480:
                self.rect.x = self.canon.rect.x - 70
        else:
            if self.rect.x < -115:
                self.rect.x = self.canon.rect.x - 70


#  Турель
class Canon(sprite.Sprite):
    def __init__(self):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = transform.scale(image.load('sprites/canon_pixian_ai.png'), (120, 90))

        # Установите ссылку на изображение прямоугольника
        self.rect = self.image.get_rect()


#  Здоровье
class Hearts(sprite.Sprite):
    def __init__(self, width, height):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = transform.scale(image.load('sprites/heart.png'), (30, 30))

        # Установите ссылку на изображение прямоугольника
        self.rect = self.image.get_rect()
        self.rect.x = width
        self.rect.y = height


#  Выстрел
class Shot(sprite.Sprite):
    def __init__(self):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = shot
        # Установите ссылку на изображение прямоугольника
        self.rect = self.image.get_rect()


# Контейнер для храненияэлементов карты
level_sprites = sprite.Group()


# Класс для рисования платформ на сцене
class Level(object):
    # Метод для рисования объектов на сцене
    def draw(self, screen):
        screen.blit(b_ground, (0, 0))
        level_sprites.draw(screen)


class Level_1(Level):
    def __init__(self, player):
        # Вызываем родительский конструктор
        Level.__init__(self)

        level = [
            [210, 32, 500, 520],
            [210, 32, 200, 420],
            [210, 32, 600, 360],
            [100, 32, 800, 540],
            [100, 32, 1000, 360],
            [100, 32, 1380, 400]
        ]

        level1 = [
            [100, 100, 1000, 550],
            [100, 100, 1300, 550]
        ]

        # Перебираем массив и добавляем каждую платформу в группу спрайтов - level_sprites
        for mg in level1:
            block = Magma()
            block.rect.x = mg[2]
            block.rect.y = mg[3]
            level_sprites.add(block)

        for platform in level:
            block1 = Platform()
            block1.rect.x = platform[2]
            block1.rect.y = platform[3]
            level_sprites.add(block1)

        c_point = CheckPoint()
        c_point.rect.x = 2000
        c_point.rect.y = 500
        level_sprites.add(c_point)

        # В первом уровне мы не будем отображать турель со снарядом и поэтому скроем их за экран
        canon = Canon()
        canon.rect.x = 1300
        canon.rect.y = 1280
        level_sprites.add(canon)

        self.bullet = Bullet(canon, player)
        self.bullet.rect.x = 1230
        self.bullet.rect.y = 885
        level_sprites.add(self.bullet)


class Level_2(Level):
    def __init__(self, player):
        # Вызываем родительский конструктор
        Level.__init__(self)

        # ширина, высота, x и y позиция
        level = [
            [210, 32, 450, 520],
            [210, 32, 650, 520],
            [210, 32, 740, 440],
            [210, 32, 850, 360],
            [100, 32, 1200, 360],
            [100, 32, 1400, 360],
            [100, 32, 1750, 427],
            [100, 32, 2100, 518]
        ]

        level1 = [
            [100, 100, 1030, 550],
            [100, 100, 1400, 550]
        ]
        # Перебираем массив и добавляем каждую платформу в группу спрайтов - level_sprites
        for mg in level1:
            block = Magma()
            block.rect.x = mg[2]
            block.rect.y = mg[3]
            level_sprites.add(block)

        for platform in level:
            block1 = Platform()
            block1.rect.x = platform[2]
            block1.rect.y = platform[3]
            level_sprites.add(block1)

        c_point = CheckPoint()
        c_point.rect.x = 2470
        c_point.rect.y = 500
        level_sprites.add(c_point)

        canon = Canon()
        canon.rect.x = 1500
        canon.rect.y = 280
        level_sprites.add(canon)

        self.bullet = Bullet(canon, player)
        self.bullet.rect.x = 1430
        self.bullet.rect.y = 285
        level_sprites.add(self.bullet)


# Основная функция прогарммы
def main(level_num):
    # Установка высоты и ширины
    size = [WIDTH, HEIGHT]
    screen = display.set_mode(size)
    image_of_death = transform.scale(image.load('sprites/death.jpg'), (450, 200))

    # Название игры
    display.set_caption("RUN and GUN")

    flag = False
    left = False
    right = False

    anim_count = 0
    level_sprites.empty()
    # Создание игрока
    player = Player(Shot())
    current_level = 1
    # Устанавка уровня
    if level_num == 1:
        current_level = Level_1(player)
    elif level_num == 2:
        current_level = Level_2(player)
    player_sprite_list = sprite.Group()

    player.rect.x = 340
    player.rect.y = HEIGHT - player.rect.height
    player_sprite_list.add(player)
    player_sprite_list.add(player.shot)

    done = True
    clock = time.Clock()
    while done:
        for event in pygame.event.get():
            if event.type == QUIT:
                done = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    main_menu()
                if player.health > 0:
                    if event.key == K_LEFT:
                        left = True
                        right = False
                        player.move_left()
                    if event.key == K_RIGHT:
                        left = False
                        right = True
                        player.move_right()
                    if event.key == pygame.K_UP:
                        player.jump()
                    if event.key == pygame.K_f:
                        player.shoot()

            if event.type == KEYUP:
                if event.key == K_SPACE:
                    level_sprites.empty()
                    flag = False
                    main(level_num)
                if event.key == K_LEFT and player.vel_x < 0:
                    left = False
                    right = False
                    player.stop(player_icon_l)
                if event.key == K_RIGHT and player.vel_x > 0:
                    left = False
                    right = False
                    player.stop(player_icon_r)

        if player.health <= 0:
            flag = True

        if anim_count + 1 > 50:
            anim_count = 0
        if left:
            player.image = frames_left[anim_count // 5]
            anim_count += 1
        elif right:
            player.image = frames_right[anim_count // 5]
            anim_count += 1
        # Обновляем игрока
        player_sprite_list.update()

        # Рисуем объекты на окне
        current_level.draw(screen)
        current_level.bullet.update()
        player_sprite_list.draw(screen)
        player.hearts_sprite_list.draw(screen)

        # Отрисовка экрана смерти
        if flag:
            screen.blit(image_of_death, (190, 220))

        clock.tick(50)

        # Обновление экрана
        display.flip()
        # Скрытие спрайта выстрела
        player.shot.rect.y = 800

    quit()


width = 800
height = 600
res = (width, height)
menu_bg = pygame.transform.scale(image.load('sprites/mainmenu_fon.jpg'), res)


# Главное меню
def main_menu():
    pygame.init()

    screen = pygame.display.set_mode(res)
    display.set_caption("RUN and GUN")

    color_text = (255, 255, 255)
    color_light = (170, 170, 170)
    color_dark = (100, 100, 100)

    level_text = pygame.font.SysFont('Corbel', 35).render('Level 1', True, color_text)
    level_text2 = pygame.font.SysFont('Corbel', 35).render('Level 2', True, color_text)

    w = width / 2
    h = height / 2
    done = True
    while done:
        mouse_xy = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = False
            # Отслеживание нажатия
            if event.type == pygame.MOUSEBUTTONDOWN:
                if w - 380 <= mouse_xy[0] <= w - 240 and h <= mouse_xy[1] <= h + 40:
                    main(1)
                elif w - 380 <= mouse_xy[0] <= w - 240 and h + 80 <= mouse_xy[1] <= h + 120:
                    main(2)

        screen.blit(menu_bg, (0, 0))

        # Отрисовка оттенка кнопок в зависимости от расположения курсора
        if w - 380 <= mouse_xy[0] <= w - 240 and h <= mouse_xy[1] <= h + 40:
            pygame.draw.rect(screen, color_light, [w - 380, h, 140, 40])
        else:
            pygame.draw.rect(screen, color_dark, [w - 380, h, 140, 40])

        if w - 380 <= mouse_xy[0] <= w - 240 and h + 80 <= mouse_xy[1] <= h + 120:
            pygame.draw.rect(screen, color_light, [w - 380, h + 80, 140, 40])
        else:
            pygame.draw.rect(screen, color_dark, [w - 380, h + 80, 140, 40])

        # Отрисовка надписи на кнопке
        screen.blit(level_text, (w - 370, h))

        screen.blit(level_text2, (w - 370, h + 80))
        pygame.display.flip()
    quit()


if __name__ == '__main__':
    main_menu()
