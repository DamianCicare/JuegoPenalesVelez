import sys  # Asegúrate de agregar el import sys arriba de todo
import pygame
import random
import os

def get_path(filename):
    """ Obtiene la ruta de los archivos para que funcione tanto en Python como en el EXE """
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)



# --- INICIALIZACIÓN SEGURA ---
pygame.mixer.pre_init(44100, -16, 2, 512) # Configuración estable para mobile
pygame.init()
pygame.mixer.init()

# Detectar pantalla completa en Android
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Velez Penales Mobile")
clock = pygame.time.Clock()
FPS = 60

# Colores
GRASS_GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
VELEZ_BLUE = (0, 51, 153)
BLACK = (0, 0, 0)
BALL_COLOR = (240, 240, 240)
YELLOW = (255, 255, 0)
SKIN = (255, 220, 180)
RED = (220, 0, 0)

# --- CARGA DE SONIDOS SEGURA ---
def get_path(filename):
    # En Android, los archivos están en el mismo directorio que el main.py
    return os.path.join(os.path.dirname(__file__), filename)

s_hinchada = None
s_silbato = None
s_gol = None

try:
    # Solo intentamos cargar si el archivo existe para evitar el crash
    if os.path.exists(get_path("hinchada.wav")):
        s_hinchada = pygame.mixer.Sound(get_path("hinchada.wav"))
        s_hinchada.play(-1)
    if os.path.exists(get_path("silbato.wav")):
        s_silbato = pygame.mixer.Sound(get_path("silbato.wav"))
    if os.path.exists(get_path("gol.wav")):
        s_gol = pygame.mixer.Sound(get_path("gol.wav"))
except Exception as e:
    print(f"Error cargando sonidos: {e}")

# --- CLASES ---
class Ball:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x, self.y = WIDTH // 2, HEIGHT * 0.85
        self.radius, self.active = 30, False
        self.dx, self.dy, self.dz, self.curve = 0, 0, 0, 0
    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), int(self.radius) + 2)
        pygame.draw.circle(surface, BALL_COLOR, (int(self.x), int(self.y)), int(self.radius))
    def update(self, wind):
        if self.active:
            self.y -= self.dy
            self.x += self.dx + self.curve + wind
            self.y += self.dz
            if self.radius > 15: self.radius -= 0.2

# --- FUNCIONES DE DIBUJO ---
def draw_detailed_player(surface, x, y):
    pygame.draw.rect(surface, WHITE, (x - 20, y, 40, 60))
    pygame.draw.polygon(surface, VELEZ_BLUE, [(x - 20, y), (x, y + 25), (x + 20, y)])
    pygame.draw.rect(surface, VELEZ_BLUE, (x - 20, y + 60, 40, 20))
    pygame.draw.circle(surface, SKIN, (x, y - 15), 15)

def draw_detailed_gk(surface, x, y):
    pygame.draw.rect(surface, (50, 50, 50), (x - 25, y, 50, 70))
    pygame.draw.rect(surface, (30, 30, 30), (x - 60, y + 10, 40, 10))
    pygame.draw.rect(surface, (30, 30, 30), (x + 20, y + 10, 40, 10))
    pygame.draw.circle(surface, SKIN, (x, y - 15), 15)

def draw_goal(surface):
    goal_w = WIDTH * 0.7
    goal_x = (WIDTH - goal_w) // 2
    pygame.draw.line(surface, WHITE, (goal_x, HEIGHT*0.4), (goal_x + goal_w, HEIGHT*0.4), 10)
    pygame.draw.line(surface, WHITE, (goal_x, HEIGHT*0.4), (goal_x, HEIGHT*0.15), 10)
    pygame.draw.line(surface, WHITE, (goal_x + goal_w, HEIGHT*0.4), (goal_x + goal_w, HEIGHT*0.15), 10)

def main():
    ball = Ball()
    gk_x = WIDTH // 2
    gk_target_x = WIDTH // 2
    aim_x, aim_y = WIDTH // 2, HEIGHT * 0.3
    power, wind = 0, random.uniform(-0.5, 0.5)
    score, msg, game_state = 0, "", "AIMING"
    is_charging = False

    # FUENTE SEGURA PARA ANDROID (None usa la default)
    font = pygame.font.Font(None, int(WIDTH * 0.08))

    running = True
    while running:
        screen.fill(GRASS_GREEN)
        draw_goal(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "AIMING":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_charging = True
                if event.type == pygame.MOUSEMOTION and not is_charging:
                    aim_x, aim_y = event.pos
                if event.type == pygame.MOUSEBUTTONUP:
                    is_charging = False
                    if s_silbato: s_silbato.play()
                    ball.active = True
                    ball.dy = 10
                    ball.dx = (aim_x - WIDTH // 2) / 25
                    ball.dz = (aim_y - HEIGHT * 0.5) / 25
                    gk_target_x = random.choice([WIDTH*0.3, WIDTH*0.5, WIDTH*0.7])
                    game_state = "KICKING"

        if game_state == "AIMING":
            if is_charging: power = min(100, power + 2)
            pygame.draw.circle(screen, RED, (int(aim_x), int(aim_y)), 15, 2)

        elif game_state == "KICKING":
            if pygame.mouse.get_pressed()[0]:
                if pygame.mouse.get_pos()[0] < WIDTH // 2: ball.curve -= 0.3
                else: ball.curve += 0.3
            
            ball.update(wind)
            gk_x += (gk_target_x - gk_x) * 0.1

            if ball.y <= HEIGHT * 0.25:
                ball.active = False
                gk_rect = pygame.Rect(gk_x - 50, HEIGHT*0.15, 100, 100)
                ball_rect = pygame.Rect(ball.x - 20, ball.y - 20, 40, 40)
                
                if gk_rect.colliderect(ball_rect): msg = "¡ATAJÓ EL ARQUERO!"
                elif (WIDTH*0.15) < ball.x < (WIDTH*0.85) and (HEIGHT*0.15) < ball.y < (HEIGHT*0.4):
                    msg = "¡GOL DE VELEZ!"; score += 1
                    if s_gol: s_gol.play()
                else: msg = "¡AFUERA!"
                game_state = "RESULT"

        draw_detailed_gk(screen, int(gk_x), int(HEIGHT * 0.2))
        ball.draw(screen)
        draw_detailed_player(screen, int(WIDTH // 2), int(HEIGHT * 0.85))

        # UI
        score_txt = font.render(f"GOLES: {score}", True, YELLOW)
        screen.blit(score_txt, (30, 30))

        if game_state == "RESULT":
            res_txt = font.render(msg, True, WHITE)
            screen.blit(res_txt, (WIDTH // 2 - res_txt.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            ball.reset(); power, game_state = 0, "AIMING"
            wind = random.uniform(-0.5, 0.5)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()