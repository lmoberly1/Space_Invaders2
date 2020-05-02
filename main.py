import pygame
import os
import random
import time

pygame.font.init()

# WINDOW, CAPTION, ICON
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
ICON = pygame.image.load(os.path.join('assets', 'spaceship.png'))
pygame.display.set_icon(ICON)

# ALIEN SHIPS
TURQ_SHIP = pygame.image.load(os.path.join('assets', 'enemy1.png'))
GREEN_SHIP = pygame.image.load(os.path.join('assets', 'enemy2.png'))
# PLAYER SHIP
PLAYER_SHIP = pygame.image.load(os.path.join('assets', 'player.png'))
# BULLET
BULLET = pygame.image.load(os.path.join('assets', 'bullet.png'))
# BACKGROUND
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'space.png')), (WIDTH, HEIGHT))

SCORE = 0

class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30 # 1/2 second

    def __init__(self, x, y, health = 100): # health = 100 makes the health variable optional
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cool_down_counter = 0
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)
    def move_bullets(self, vel, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    def shoot(self, add_x, add_y):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x + add_x, self.y + add_y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_width()



class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP
        self.bullet_img = BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, vel, objs):
        global SCORE
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        SCORE += 1
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
    def draw(self, window):
        super().draw(window)
        self.health_bar(window)
    def health_bar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 5))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 5))


class Enemy(Ship):
    COLOR_MAP = {
                "turq": (TURQ_SHIP),
                "green": (GREEN_SHIP),
                }
    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img = self.COLOR_MAP[color]
        self.bullet_img = pygame.transform.rotate(BULLET,180)
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.x_vel = random.choice([-1, 1])
    def move(self, vel):
        self.y += vel
        if self.x > 0 and self.x < WIDTH - self.get_width():
            self.x += self.x_vel
        elif self.x == 0 or self.x == WIDTH - self.get_width():
            self.x_vel *= -1
            self.x += self.x_vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None # returns (x,y) of point of intersection


def main():
    global SCORE

    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)
    # ENEMIES
    enemies = []
    wave_length = 5
    enemy_vel = .7
    # PLAYER
    player_vel = 5
    bullet_vel = 8
    player = Player(300, 650)
    # GAME OVER
    clock = pygame.time.Clock()
    lost_count = 0

    # REDRAW WINDOW
    def redraw_window():
        # BACKGROUND
        WIN.blit(BG, (0,0))
        # TEXT
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {SCORE}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2 - 20, 10))
        # ENEMY DRAW
        for enemy in enemies:
            enemy.draw(WIN)
        # PLAYER DRAW
        player.draw(WIN)
        # UPDATE DISPLAY
        pygame.display.update()

    # GAME OVER FUNCTION
    def game_over():
        global SCORE
        waiting = True
        while waiting:
            clock.tick(FPS)
            lost_label = lost_font.render(f"YOU LOST!", 1, (255,255,255), 10)
            reset_label = lost_font.render(f"Press SPACE to play again.", 1, (255,255,255), 10)
            WIN.blit(BG, (0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2 - lost_label.get_height()/2))
            WIN.blit(reset_label, (WIDTH/2 - reset_label.get_width()/2, HEIGHT/2 + lost_label.get_height() + reset_label.get_height()/2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
        SCORE = 0 
        main_menu()

    # GAME LOOP
    while run:
        clock.tick(FPS)
        redraw_window()

        # GAME OVER
        if lives <= 0 or player.health <= 0:
            game_over()
            pygame.time.wait(3000)
            main_menu()

        # ENEMY SPAWN
        if len(enemies) == 0:
            wave_length += 5
            level += 1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 50), random.randrange(-1500, -100), random.choice(["turq", "green"]))
                enemies.append(enemy)
        # EVENTS
        for event in pygame.event.get():
            # QUIT
            if event.type == pygame.QUIT:
                quit()
        # KEYS
        keys = pygame.key.get_pressed() # creates dictionary of the keys that are pressed
        if keys[pygame.K_a] and player.x - player_vel > 0: # LEFT
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width()< WIDTH: # RIGHT
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # UP
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # DOWN (+10 ensures that health bar won't go past health)
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot(15, -10)
        # ENEMY MOVEMENT
        for enemy in enemies[:]: # makes a copy of the enemies list
            enemy.move(enemy_vel)
            enemy.move_bullets(bullet_vel, player)
            if random.randrange(0, 3*60) == 1: # should shoot every 2ish seconds
                enemy.shoot(15, 55)

            if collide(enemy, player):
                player.health -= 10
                SCORE += 1
                enemies.remove(enemy)
            elif enemy.y > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_bullets(-bullet_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True

    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press SPACE to begin.", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, HEIGHT/2 - title_label.get_height()/2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()
    pygame.quit()


main_menu()
