import pygame
import sys
import random
import math

print('loading pygame...')
# Initialize Pygame
pygame.init()
print('pygame loaded')
print('')
print('Loading Game...')
print('')
# Screen dimensions
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball Shooter (v0.1)")
print('set screen size to 1080x720')
print('')
print('loading colors...')
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
print('colors loaded')

# Paddle
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 12
PADDLE_SPEED = 8


# Ball
BALL_RADIUS = 10
BALL_SPEED = 8


# Bricks
BRICK_ROWS = 6
BRICK_COLS = 15
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
BRICK_GAP = 12
BRICK_OFFSET_TOP = 60

print('loading audio files...')
#background music
print('')
print('loading background music...')
try:
    pygame.mixer.music.load("audio/music.mp3") # Make sure this path is correct
    print("Background music 'music.mp3' loaded.")
    print('loaded background music')
    pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
    pygame.mixer.music.play(-1)         # Play indefinitely (-1 means loop forever)
except pygame.error as e:
    print(f"Failed to load or play background music: {e}")
print('')
print('loading sound effects...')
pygame.mixer.init()
try:
    lose = pygame.mixer.Sound("audio/fail.wav")
    print('loaded fail.wav')
except pygame.error:
    print("Failed to load sound file 'fail.wav'. Make sure the file exists in the 'audio' folder.")
    lose = None  # Set to None to prevent errors later
try:
    win = pygame.mixer.Sound("audio/life.wav")
    print('loaded life.wav')
except pygame.error:
    print("Failed to load sound file 'life.wav'. Make sure the file exists in the 'audio' folder.")
    win = None  # Set to None to prevent errors later

print('all audio files loaded')
print('')
print('oading font...')
# Font
font = pygame.font.SysFont('Arial', 24)
large_font = pygame.font.SysFont('Arial', 36) # For high score display
print('loaded fonts')
print('')
print('searching for highscore.txt in /ball-shooter...')
# High Score File
HIGHSCORE_FILE = "highscore.txt"
print('found highscore.txt')
print('loaded highscore.text')
print('')
def load_highscore():
    """Loads the high score from a file."""
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0 # Default high score if file not found or empty/corrupt

def save_highscore(score):
    """Saves the high score to a file."""
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


class Paddle:
    def __init__(self):
        self.rect = pygame.Rect((SCREEN_WIDTH - PADDLE_WIDTH)//2,
                               SCREEN_HEIGHT - 50,
                               PADDLE_WIDTH, PADDLE_HEIGHT)


    def move(self, direction):
        if direction == "left":
            self.rect.x -= PADDLE_SPEED
        elif direction == "right":
            self.rect.x += PADDLE_SPEED
        self.rect.x = max(self.rect.x, 0)
        self.rect.x = min(self.rect.x, SCREEN_WIDTH - self.rect.width)


    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)


class Ball:
    def __init__(self):
        self.reset()


    def reset(self):
        global BALL_SPEED
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        angle = random.uniform(-1, 1)
        speed = BALL_SPEED
        self.dx = speed * angle
        self.dy = -abs((speed ** 2 - self.dx ** 2) ** 0.5) if abs(angle) < 1 else -speed * 0.5
        if abs(self.dx) < 2:
            self.dx = 2 * (1 if self.dx >= 0 else -1)


    def move(self):
        self.x += self.dx
        self.y += self.dy


    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), BALL_RADIUS)


    def rect(self):
        return pygame.Rect(self.x - BALL_RADIUS, self.y - BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)


class Brick:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = color


    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)


class Powerup:
    WIDTH = 32
    HEIGHT = 16
    FALL_SPEED = 4


    TYPES = ['widen', 'shrink', 'slow', 'fast', 'multiball']


    COLOR_MAP = {
        'widen': (0, 255, 255),
        'shrink': (255, 0, 255),
        'slow': (128, 255, 128),
        'fast': (255, 128, 0),
        'multiball': (255, 255, 128),
    }


    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, Powerup.WIDTH, Powerup.HEIGHT)
        self.type = type


    def move(self):
        self.rect.y += Powerup.FALL_SPEED


    def draw(self, surface):
        pygame.draw.rect(surface, Powerup.COLOR_MAP[self.type], self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        label = font.render(self.type[0].upper(), True, BLACK)
        surface.blit(label, (self.rect.x + 8, self.rect.y + 2))


def create_bricks():
    bricks = []
    colors = [YELLOW, GREEN, BLUE, RED, WHITE, (255, 128, 0)]
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = col * (BRICK_WIDTH + BRICK_GAP) + BRICK_GAP
            y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_GAP)
            brick = Brick(x, y, colors[row % len(colors)])
            bricks.append(brick)
    return bricks


def set_ball_speed(ball, new_speed):
    speed = (ball.dx**2 + ball.dy**2) ** 0.5
    if speed != 0:
        factor = new_speed / speed
        ball.dx *= factor
        ball.dy *= factor


def apply_powerup(powerup_type, paddle, balls):
    global PADDLE_WIDTH, BALL_SPEED
    if powerup_type == 'widen':
        PADDLE_WIDTH = min(PADDLE_WIDTH + 100, SCREEN_WIDTH)
        paddle.rect.width = PADDLE_WIDTH
        paddle.rect.x = max(0, min(paddle.rect.x, SCREEN_WIDTH - paddle.rect.width))
    elif powerup_type == 'shrink':
        PADDLE_WIDTH = max(PADDLE_WIDTH - 100, 60)
        paddle.rect.width = PADDLE_WIDTH
        paddle.rect.x = max(0, min(paddle.rect.x, SCREEN_WIDTH - paddle.rect.width))
    elif powerup_type == 'slow':
        BALL_SPEED = max(BALL_SPEED - 2, 4)
        for ball in balls:
            set_ball_speed(ball, BALL_SPEED)
    elif powerup_type == 'fast':
        BALL_SPEED += 2
        for ball in balls:
            set_ball_speed(ball, BALL_SPEED)
    elif powerup_type == 'multiball':
        if len(balls) < 6:
            orig = balls[0]
            for _ in range(2):
                new_ball = Ball()
                new_ball.x = orig.x
                new_ball.y = orig.y
                angle = random.uniform(-1, 1)
                speed = BALL_SPEED
                new_ball.dx = speed * angle
                new_ball.dy = -abs((speed ** 2 - new_ball.dx ** 2) ** 0.5) if abs(angle) < 1 else -speed * 0.5
                if abs(new_ball.dx) < 2:
                    new_ball.dx = 2 * (1 if new_ball.dx >= 0 else -1)
                balls.append(new_ball)


def next_level(level):
    global paddle, balls, bricks, BRICK_ROWS, PADDLE_WIDTH, BALL_SPEED
    BRICK_ROWS = 6 + (level - 1)
    if BRICK_ROWS > 12:
        BRICK_ROWS = 12
    PADDLE_WIDTH = max(120 - (level - 1)*12, 60)
    BALL_SPEED = 8 + (level - 1) * 2
    paddle = Paddle()
    balls = [Ball()]
    bricks = create_bricks()


def draw_text(surface, text, x, y, color=WHITE, font_obj=None):
    if font_obj is None:
        font_obj = font
    text_surf = font_obj.render(text, True, color)
    rect = text_surf.get_rect(center=(x, y))
    surface.blit(text_surf, rect)

print('game loaded')

def main():
    clock = pygame.time.Clock()
    level = 1
    score = 0
    highscore = load_highscore() # Load high score at the start
    next_level(level)
    running = True
    game_over = False
    win = False
    powerups = []
    global paddle, balls, bricks


    while running:
        SCREEN.fill(BLACK)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            paddle.move("left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            paddle.move("right")


        if not game_over:
            for ball in balls[:]:
                ball.move()
                if ball.x - BALL_RADIUS <= 0 or ball.x + BALL_RADIUS >= SCREEN_WIDTH:
                    ball.dx *= -1
                if ball.y - BALL_RADIUS <= 0:
                    ball.dy *= -1
                if ball.rect().colliderect(paddle.rect) and ball.dy > 0:
                    offset = (ball.x - paddle.rect.centerx) / (paddle.rect.width / 2)
                    max_angle = 60
                    angle = offset * max_angle
                    speed = (ball.dx**2 + ball.dy**2) ** 0.5
                    rad = math.radians(angle)
                    ball.dx = speed * math.sin(rad)
                    ball.dy = -abs(speed * math.cos(rad))
                hit_index = ball.rect().collidelist([brick.rect for brick in bricks])
                if hit_index != -1:
                    hit_brick = bricks.pop(hit_index)
                    score += 10 # Increase score when a brick is hit
                    bx, by = ball.x, ball.y
                    brick_rect = hit_brick.rect
                    overlap = [abs(brick_rect.left - (bx + BALL_RADIUS)),
                               abs(brick_rect.right - (bx - BALL_RADIUS)),
                               abs(brick_rect.top - (by + BALL_RADIUS)),
                               abs(brick_rect.bottom - (by - BALL_RADIUS))]
                    if min(overlap[:2]) < min(overlap[2:]):
                        ball.dx *= -1
                    else:
                        ball.dy *= -1
                    if random.random() < 0.25:
                        ptype = random.choice(Powerup.TYPES)
                        powerup = Powerup(hit_brick.rect.centerx - Powerup.WIDTH//2,
                                          hit_brick.rect.centery - Powerup.HEIGHT//2, ptype)
                        powerups.append(powerup)
                if ball.y - BALL_RADIUS > SCREEN_HEIGHT:
                    balls.remove(ball)
                    if not balls:
                        game_over = True


            if not bricks:
                win = True
                game_over = True


        paddle.draw(SCREEN)
        for ball in balls:
            ball.draw(SCREEN)
        for brick in bricks:
            brick.draw(SCREEN)
        for powerup in powerups[:]:
            powerup.move()
            powerup.draw(SCREEN)
            if powerup.rect.top > SCREEN_HEIGHT:
                powerups.remove(powerup)
            elif powerup.rect.colliderect(paddle.rect):
                apply_powerup(powerup.type, paddle, balls)
                powerups.remove(powerup)

        # Display current score and high score
        draw_text(SCREEN, f"Score: {score}", SCREEN_WIDTH - 80, 20, WHITE)
        draw_text(SCREEN, f"High Score: {highscore}", 100, 20, WHITE)


        if game_over:
            if score > highscore: # Check for new high score
                highscore = score
                save_highscore(highscore) # Save the new high score
                draw_text(SCREEN, "NEW HIGH SCORE!", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, YELLOW, large_font)

            if win:
                draw_text(SCREEN, f"Level {level} Complete! Press R", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, GREEN)
                if win: # Only play if the sound was loaded successfully
                    win.play()
            else:
                draw_text(SCREEN, "Game Over! Press R to Restart", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, RED)
            if keys[pygame.K_r]:
                level = level + 1 if win else 1
                score = 0 # Reset score for new game/level
                powerups.clear()
                next_level(level)
                game_over = False
                win = False
            if lose: # Only play if the sound was loaded successfully
                lose.play()

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()