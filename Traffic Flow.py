import pygame
import random
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
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


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 800
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гоночка")
pygame.display.set_icon(load_image('black_pickup.png'))

clock = pygame.time.Clock()

pygame.mixer.music.load("gamegg.mp3")

pygame.mixer.music.play(-1)

font = pygame.font.Font(None, 36)

game_state = "start"  # добавляем переменную для отслеживания состояния игры


class Button:
    def __init__(self, name, x, y, width, height, action, k=None):
        self.image = load_image(name, k)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = pygame.Rect(x, y, x + width, y + height)
        self.action = action

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()


class Fon:
    def __init__(self, name, k=None):
        self.image = load_image(name, k)
        self.image = pygame.transform.scale(self.image, (400, 1600))
        self.fon_list = []
        self.fon_speed = 4

    def draw_fon(self):
        for fon in self.fon_list:
            screen.blit(self.image, (0, fon[1]))

    def roll(self):
        if len(self.fon_list) < 5:
            new_fon = [0, -400]
            self.fon_list.append(new_fon)

        if len(self.fon_list) < 5:
            new_fon = [0, -1600]
            self.fon_list.append(new_fon)

        for fon in self.fon_list:
            fon[1] += self.fon_speed
            if fon[1] > HEIGHT:
                self.fon_list.remove(fon)
                if len(self.fon_list) < 5:
                    new_fon = [0, -400]
                    self.fon_list.append(new_fon)
                    new_fon = [0, -1600]
                    self.fon_list.append(new_fon)
                    new_fon = [0, -3200]
                    self.fon_list.append(new_fon)


class Score:
    def __init__(self, name):
        self.file = name
        self.score = 0

    def get_best_score(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                best_score = int(f.read())
        else:
            best_score = 0
        return best_score

    def draw_score(self):
        score_text = font.render("Score: " + str(self.score), True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    def draw_best_score(self):
        best_score = self.get_best_score()
        best_score_text = font.render("Best Score: " + str(best_score), True, (255, 255, 255))
        screen.blit(best_score_text, (10, 50))

    def save_best_score(self, score):
        best_score = self.get_best_score()
        if score > best_score:
            with open(self.file, "w") as f:
                f.write(str(score))


class PlayerCar:
    def __init__(self, name):
        self.car_img = load_image(name)
        self.car_img = pygame.transform.scale(self.car_img, (50, 80))
        self.car_x = WIDTH // 2 - self.car_img.get_width() // 2
        self.car_y = HEIGHT - self.car_img.get_height()
        self.car_speed = 5

    def move(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.car_x > 0:
            self.car_x -= self.car_speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.car_x < WIDTH - self.car_img.get_width():
            self.car_x += self.car_speed


class EnemyCar:
    def __init__(self, name):
        self.car2_img = load_image(name)
        self.car2_img = pygame.transform.scale(self.car2_img, (50, 80))
        self.car2_speed = 9
        self.car2_list = []
        self.last_pos = None
        self.pos_width = [18, 118, 230, 335]

    def spawn(self):
        if len(self.car2_list) < 3 and random.randint(0, 100) < 5:
            num_new_cars = random.randint(1, 3 - len(self.car2_list))
            for _ in range(num_new_cars):
                if not self.pos_width or (self.last_pos in self.pos_width and len(self.pos_width) == 1):
                    self.pos_width = [18, 118, 230, 335]

                new_pos = random.choice(self.pos_width)
                while new_pos == self.last_pos:
                    new_pos = random.choice(self.pos_width)

                self.last_pos = new_pos
                self.pos_width.remove(new_pos)

                new_car2 = [new_pos + random.randrange(-10, 10), 0]
                self.car2_list.append(new_car2)


def exit_game():
    pygame.quit()
    pygame.mixer.quit()
    exit()


def menu():
    global game_state
    game_state = 'start'


class Game:
    def __init__(self):
        self.fon = Fon('fon.jpg', -1)
        self.counter = Score('score.txt')
        self.player = PlayerCar('car.png')
        self.enemy = EnemyCar('car2.png')
        self.running = False
        self.fire_animation = [
            load_image('fire/fire1.png'),
            load_image('fire/fire2.png'),
            load_image('fire/fire3.png'),
            load_image('fire/fire4.png')
        ]
        self.fire_animation = [pygame.transform.scale(img, self.player.car_img.get_size())
                               for img in self.fire_animation]
        self.fire_index = 0
        self.fire_timer = 0
        self.fire_delay = 5

    def play_fire_animation(self):
        self.player.car_img = self.fire_animation[self.fire_index]
        self.fire_index = (self.fire_index + 1) % len(self.fire_animation)

    def run(self):
        global game_state
        self.running = True
        game_state = 'running'
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    pygame.mixer.quit()
                    exit()

            screen.fill((0, 0, 0))

            self.player.move()

            for car2 in self.enemy.car2_list:
                car2[1] += self.enemy.car2_speed
                if car2[1] > HEIGHT:
                    self.enemy.car2_list.remove(car2)
                    self.counter.score += 1
                    if self.counter.score % 15 == 0:
                        self.enemy.car2_speed += 1
                        self.player.car_speed += 1
                        self.fon.fon_speed += 1

            self.enemy.spawn()

            for car2 in self.enemy.car2_list:
                car2_rect = pygame.Rect(car2[0], car2[1], self.enemy.car2_img.get_width(),
                                        self.enemy.car2_img.get_height())
                car_rect = pygame.Rect(self.player.car_x, self.player.car_y, self.player.car_img.get_width(),
                                       self.player.car_img.get_height())
                if car_rect.colliderect(car2_rect):
                    game_state = "game_over"
                    self.counter.save_best_score(self.counter.score)
                    self.play_fire_animation()
                    self.running = False

            self.fon.draw_fon()

            screen.blit(self.player.car_img, (self.player.car_x, self.player.car_y))

            for car2 in self.enemy.car2_list:
                screen.blit(self.enemy.car2_img, (car2[0], car2[1]))

            self.fon.roll()

            screen.blit(self.player.car_img, (self.player.car_x, self.player.car_y))

            self.counter.draw_score()
            self.counter.draw_best_score()

            pygame.display.flip()
            clock.tick(FPS)

    def start_game(self):
        self.player.car_img = load_image('car.png')
        self.player.car_img = pygame.transform.scale(self.player.car_img, (50, 80))
        self.player.car_x = WIDTH // 2 - self.player.car_img.get_width() // 2
        self.player.car_y = HEIGHT - self.player.car_img.get_height()
        self.enemy.car2_list = []
        self.fon.fon_list = []
        self.counter.score = 0
        self.enemy.car2_speed = 9
        self.player.car_speed = 5
        self.fon.fon_speed = 4
        self.run()


menu_img = load_image('menu.jpg')
menu_img = pygame.transform.scale(menu_img, (400, 800))
menu_rect = menu_img.get_rect(topleft=(0, 0))

start_button = Button('start_button.png', 100, 100, 200, 100, Game().start_game)
restart_button = Button('restart_button.png', 87, 100, 228, 130, Game().start_game)
exit_button = Button('exit_button.png', 88, 300, 225, 130, exit_game)
menu_button = Button('menu_button.png', 88, 200, 225, 130, menu)

while True:
    if game_state == 'start':
        screen.blit(menu_img, menu_rect.topleft)
        start_button.draw(screen)
        exit_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                start_button.check_click(event.pos)
                exit_button.check_click(event.pos)
            if event.type == pygame.QUIT:
                pygame.quit()
                pygame.mixer.quit()
    if game_state == 'game_over':
        restart_button.draw(screen)
        exit_button.draw(screen)
        menu_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                restart_button.check_click(event.pos)
                menu_button.check_click(event.pos)
                exit_button.check_click(event.pos)
            if event.type == pygame.QUIT:
                pygame.quit()
                pygame.mixer.quit()
    pygame.display.flip()