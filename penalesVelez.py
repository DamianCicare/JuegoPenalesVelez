import pygame
import random
import math

# --- CONFIGURACIÓN ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colores
GRASS_GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
VELEZ_BLUE = (0, 51, 153)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
BALL_COLOR = (240, 240, 240)
YELLOW = (255, 255, 0) 
GREY = (150, 150, 150)
SKIN = (255, 220, 180)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vélez Sarsfield - Simulador con Hinchada")
clock = pygame.time.Clock()

# --- SONIDOS ---
def load_sound(file):
    try: return pygame.mixer.Sound(file)
    except: return None

s_hinchada = load_sound("hinchada.wav")
s_silbato = load_sound("silbato.wav")
s_gol = load_sound("gol.wav")

if s_hinchada: s_hinchada.play(-1)

# --- CLASES ---

class Ball:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x, self.y = WIDTH // 2, 520
        self.radius, self.active = 14, False
        self.dx, self.dy, self.dz, self.curve = 0, 0, 0, 0
    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), int(self.radius) + 2)
        pygame.draw.circle(surface, BALL_COLOR, (int(self.x), int(self.y)), int(self.radius))
    def update(self, wind):
        if self.active:
            self.y -= self.dy
            self.x += self.dx + self.curve + wind
            self.y += self.dz 
            if self.radius > 7: self.radius -= 0.12

class Confetti:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.color = random.choice([WHITE, VELEZ_BLUE, YELLOW])
        self.speed = random.randint(3, 6)
        self.angle = random.uniform(0, math.pi * 2)

    def update(self):
        self.y += self.speed
        self.x += math.sin(self.angle) * 2
        self.angle += 0.1
        if self.y > HEIGHT: self.y = -10

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, 6, 6))

# --- DIBUJO DE PERSONAJES ---

def draw_detailed_player(surface, x, y):
    pygame.draw.rect(surface, WHITE, (x - 30, y + 5, 10, 30))
    pygame.draw.rect(surface, WHITE, (x + 20, y + 5, 10, 30))
    pygame.draw.rect(surface, WHITE, (x - 20, y, 40, 60))
    pygame.draw.polygon(surface, VELEZ_BLUE, [(x - 20, y), (x, y + 25), (x + 20, y)])
    pygame.draw.rect(surface, VELEZ_BLUE, (x - 20, y + 60, 40, 20))
    pygame.draw.rect(surface, SKIN, (x - 15, y + 80, 10, 15))
    pygame.draw.rect(surface, SKIN, (x + 5, y + 80, 10, 15))
    pygame.draw.circle(surface, SKIN, (x, y - 15), 15)
    f = pygame.font.SysFont("Arial", 16, bold=True)
    surface.blit(f.render("10", True, VELEZ_BLUE), (x-8, y+35))

def draw_detailed_gk(surface, x, y):
    pygame.draw.rect(surface, (30, 30, 30), (x - 50, y + 10, 30, 10))
    pygame.draw.rect(surface, (30, 30, 30), (x + 20, y + 10, 30, 10))
    pygame.draw.rect(surface, (50, 50, 50), (x - 20, y, 40, 60))
    pygame.draw.rect(surface, (30, 30, 30), (x - 18, y + 60, 15, 25))
    pygame.draw.rect(surface, (30, 30, 30), (x + 3, y + 60, 15, 25))
    pygame.draw.circle(surface, SKIN, (x, y - 10), 15)

def draw_goal(surface):
    for i in range(200, 601, 25): pygame.draw.line(surface, GREY, (i, 150), (i, 300), 1)
    for j in range(150, 301, 20): pygame.draw.line(surface, GREY, (200, j), (600, j), 1)
    pygame.draw.line(surface, WHITE, (200, 305), (200, 150), 10) 
    pygame.draw.line(surface, WHITE, (600, 305), (600, 150), 10) 
    pygame.draw.line(surface, WHITE, (200, 150), (600, 150), 10) 

# --- LÓGICA PRINCIPAL ---

def main():
    ball = Ball()
    gk_x, gk_y = WIDTH // 2, 190
    gk_target_x, gk_target_y = WIDTH // 2, 190
    aim_x, aim_y = WIDTH // 2, 225
    power, wind = 0, random.uniform(-1.2, 1.2)
    score, msg, game_state = 0, "", "WAITING"
    whistle_played, is_charging = False, False
    history, rep_idx = [], 0.0
    
    # Lista de papelitos para el festejo
    celebration_confetti = [Confetti() for _ in range(100)]
    celebration_timer = 0

    running = True
    while running:
        screen.fill(GRASS_GREEN)
        draw_goal(screen)
        
        # Viento UI
        v_color = RED if abs(wind) > 0.9 else WHITE
        pygame.draw.line(screen, v_color, (WIDTH//2, 60), (WIDTH//2 + wind*50, 60), 4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if game_state == "AIMING":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: is_charging = True
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                    is_charging = False
                    if s_silbato: s_silbato.play()
                    ball.active, ball.dy = True, 6 
                    ball.dx = (aim_x - WIDTH // 2) / 45
                    ball.dz = (aim_y - 350) / 45 
                    gk_target_x = random.choice([WIDTH//2-135, WIDTH//2, WIDTH//2+135])
                    gk_target_y = random.choice([155, 205])
                    game_state = "KICKING"; history = []

        # --- ESTADOS DEL JUEGO ---
        if game_state == "WAITING":
            if not whistle_played:
                if s_silbato: s_silbato.play(); whistle_played = True
                pygame.time.delay(500)
            game_state = "AIMING"

        elif game_state == "AIMING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and aim_x > 185: aim_x -= 4
            if keys[pygame.K_RIGHT] and aim_x < 615: aim_x += 4
            if keys[pygame.K_UP] and aim_y > 140: aim_y -= 4
            if keys[pygame.K_DOWN] and aim_y < 310: aim_y += 4
            if is_charging: power = min(100, power + 2)
            pygame.draw.line(screen, RED, (aim_x-10, aim_y), (aim_x+10, aim_y), 2)
            pygame.draw.line(screen, RED, (aim_x, aim_y-10), (aim_x, aim_y+10), 2)

        elif game_state == "KICKING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: ball.curve -= 0.16
            if keys[pygame.K_RIGHT]: ball.curve += 0.16
            ball.update(wind)
            gk_x += (gk_target_x - gk_x) * 0.12
            gk_y += (gk_target_y - gk_y) * 0.12
            history.append((ball.x, ball.y, ball.radius, gk_x, gk_y))

            if ball.y <= 280:
                ball.active = False
                gk_rect = pygame.Rect(gk_x - 45, gk_y, 90, 95)
                ball_rect = pygame.Rect(ball.x - 10, ball.y - 10, 20, 20)
                if gk_rect.colliderect(ball_rect): 
                    msg = "¡ATAJADA!"; game_state = "REPLAY"
                elif 205 < ball.x < 595 and 155 < ball.y < 300:
                    if power > 88 and ball.y < 175: 
                        msg = "¡POR ARRIBA!"; game_state = "REPLAY"
                    else:
                        msg = "GOL"; score += 1
                        if s_gol: s_gol.play()
                        game_state = "CELEBRATION"
                        celebration_timer = pygame.time.get_ticks()
                else: 
                    msg = "AFUERA"; game_state = "REPLAY"
                rep_idx = 0.0

        elif game_state == "CELEBRATION":
            # Animación de Hinchada
            for p in celebration_confetti:
                p.update(); p.draw(screen)
            
            # Dibujar trapos/banderas moviéndose abajo
            for i in range(0, WIDTH, 120):
                offset = math.sin(pygame.time.get_ticks() * 0.01 + i) * 20
                pygame.draw.rect(screen, VELEZ_BLUE, (i, 500 + offset, 60, 200))
                pygame.draw.rect(screen, WHITE, (i+60, 520 - offset, 60, 200))

            f_goal = pygame.font.SysFont("Impact", 120)
            goal_txt = f_goal.render("¡GOL!", True, YELLOW)
            screen.blit(goal_txt, (WIDTH//2 - goal_txt.get_width()//2, HEIGHT//2-100))

            # Después de 3 segundos de festejo, ir a repetición
            if pygame.time.get_ticks() - celebration_timer > 3000:
                game_state = "REPLAY"

        elif game_state == "REPLAY":
            if int(rep_idx) < len(history):
                hx, hy, hr, hgk_x, hgk_y = history[int(rep_idx)]
                draw_detailed_gk(screen, hgk_x, hgk_y)
                pygame.draw.circle(screen, BLACK, (int(hx), int(hy)), int(hr)+2)
                pygame.draw.circle(screen, BALL_COLOR, (int(hx), int(hy)), int(hr))
                if (pygame.time.get_ticks() // 200) % 2 == 0:
                    font_rep = pygame.font.SysFont("Impact", 35)
                    screen.blit(font_rep.render("[R] REPETICIÓN", True, RED), (20, 60))
                rep_idx += 0.3
            else: game_state = "RESULT"

        # --- DIBUJO ESTÁNDAR ---
        if game_state not in ["REPLAY", "CELEBRATION"]:
            draw_detailed_gk(screen, gk_x, gk_y)
            ball.draw(screen)
            draw_detailed_player(screen, WIDTH//2-80, 480)

        # Barra Potencia
        pygame.draw.rect(screen, BLACK, (WIDTH//2-50, 560, 100, 15), 2)
        pygame.draw.rect(screen, RED, (WIDTH//2-50, 560, power, 15))
        f_gui = pygame.font.SysFont("Arial", 20, bold=True)
        screen.blit(f_gui.render(f"GOLES: {score}", True, YELLOW), (20, 20))

        if game_state == "RESULT":
            f_big = pygame.font.SysFont("Impact", 100)
            res_txt = f_big.render(msg, True, YELLOW if "GOL" in msg else RED)
            screen.blit(res_txt, (WIDTH//2 - res_txt.get_width()//2, HEIGHT//2-100))
            pygame.display.flip(); pygame.time.delay(2000)
            ball.reset(); power, aim_x, aim_y = 0, WIDTH//2, 225
            gk_x, gk_y, whistle_played = WIDTH//2, 190, False
            wind = random.uniform(-1.2, 1.2); game_state = "WAITING"

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__": main()