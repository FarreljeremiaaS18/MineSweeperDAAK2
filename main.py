import pygame
import sys
import random

#Display Setting
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
GRAY = (192, 192, 192)
DARK_GREY = (128, 128, 128)

#Number Colors
NUMBER_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128)
    }

CELL_SIZE = 30
TOP_BAR_HEIGHT = 60 #status bar height

class MinesweeperGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 30, bold=True)
        self.state = 'MENU'  # MENU, PLAYING, GAME_OVER, WIN
        self.screen = pygame.display.set_mode((400, 300)) #Ukuran menu awal
    
    #Level Initialization
    def init_level(self, difficulty):
        if difficulty == 1: #Easy
            self.rows, self.cols, self.mines = 9, 9, 10
        elif difficulty == 2: #Medium
            self.rows, self.cols, self.mines = 16, 16, 40
        elif difficulty == 3: #Hard
            self.rows, self.cols, self.mines = 16, 30, 99
        
        #Resize Screen Based on Level
        self.width = self.cols * CELL_SIZE
        self.height = (self.rows * CELL_SIZE) + TOP_BAR_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))

        #set data
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)] #0=empty, -1=mine
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False
        self.win = False
        self.place_mines()
        self.state = "PLAYING"

    def place_mines(self):
        count = 0
        while count < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.grid[r][c] != -1:
                self.grid[r][c] = -1
                count += 1
    
    def calculate_numbers(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    continue

                #hitung bom di 8 tetangga
                count = 0
                for i in range(max(0, r-1), min(self.rows, r+2)):
                    for j in range(max(0, c-1), min(self.cols, c+2)):
                        if self.grid[i][j] == -1:
                            count += 1
                self.grid[r][c] = count
    

    #DFS
    def flood_fill(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if self.revealed[r][c] or self.flagged[r][c]:
            return
        self.revealed[r][c] = True

        #Jika sel kosong, lanjutkan ke tetangga
        if self.grid[r][c] == 0:
            for i in range(max(0, r-1), min(self.rows, r+2)):
                for j in range(max(0, c-1), min(self.cols, c+2)):
                        self.flood_fill(i, j)
    
    def handle_click(self, pos, button):
       if self.state != "PLAYING": return

       x, y = pos
       if y < TOP_BAR_HEIGHT: return #Klik di status bar diabaikan
       
       r = (y - TOP_BAR_HEIGHT) // CELL_SIZE
       c = x // CELL_SIZE

       if button == 1: # Left Click (Buka)
            if self.flagged[r][c]: return
            
            if self.grid[r][c] == -1: # Kena Bom
                self.revealed[r][c] = True
                self.game_over = True
                self.state = "GAMEOVER"
                self.reveal_all_mines()
            else:
                self.flood_fill(r, c)
                self.check_win()

       elif button == 3: # Right Click (Flag)
            if not self.revealed[r][c]:
                self.flagged[r][c] = not self.flagged[r][c]

    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    self.revealed[r][c] = True

    def check_win(self):
        count_revealed = sum(row.count(True) for row in self.revealed)
        total_safe_cells = (self.rows * self.cols) - self.mines
        if count_revealed == total_safe_cells:
            self.win = True
            self.state = "WIN"
    def draw(self):
        self.screen.fill(GRAY)
        
        #Draw Menu
        if self.state == "MENU":
            self.screen.fill(DARK_GREY)
            title = self.large_font.render("MINESWEEPER", True, WHITE)
            t1 = self.font.render("BEGINNER", True, WHITE)
            t2 = self.font.render("INTERMEDIATE", True, WHITE)
            t3 = self.font.render("EXPERT", True, WHITE)
            
            self.screen.blit(title, (100, 50))
            self.screen.blit(t1, (140, 120))
            self.screen.blit(t2, (140, 160))
            self.screen.blit(t3, (140, 200))
            return
        
        #status bar
        pygame.draw.rect(self.screen, DARK_GREY, (0, 0, self.width, TOP_BAR_HEIGHT))
        msg = ""
        if self.state == "PLAYING":
            msg = "GudLuck!"
        elif self.state == "GAMEOVER":
            msg = "BOOM! Game Over!"
        elif self.state == "WIN":
            msg = "You Win!"
        text_status = self.large_font.render(msg, True, WHITE)
        self.screen.blit(text_status, (10, 20))

        #GRID
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * CELL_SIZE, TOP_BAR_HEIGHT + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if self.revealed[r][c]:
                    pygame.draw.rect(self.screen, WHITE, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1) #bordernya

                    val = self.grid[r][c]
                    if val == -1: #bom (black dots)
                        pygame.draw.circle(self.screen, BLACK, rect.center, CELL_SIZE // 4)
                    elif val > 0: #angka
                        text = self.font.render(str(val), True, NUMBER_COLORS.get(val, BLACK))
                        text_rect = text.get_rect(center=rect.center)
                        self.screen.blit(text, text_rect)
                else:
                    #kotak tertutup
                    pygame.draw.rect(self.screen, Grey_3D_Up := (220, 220, 220), rect)
                    pygame.draw.rect(self.screen, DARK_GREY, rect, 2) #bordernya

                    if self.flagged[r][c]: #flag (segitiga merah)
                        p1 = (rect.centerx - 5, rect.centery - 5)
                        p2 = (rect.centerx + 5, rect.centery)
                        p3 = (rect.centerx - 5, rect.centery + 5)
                        pygame.draw.polygon(self.screen, RED, [p1, p2, p3])
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.state == "MENU":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            self.init_level(1) #Easy
                        elif event.key == pygame.K_2:
                            self.init_level(2) #Medium
                        elif event.key == pygame.K_3:
                            self.init_level(3) #Hard
                    
                    elif self.state in ["PLAYING", "GAMEOVER", "WIN"]:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.handle_click(event.pos, event.button)
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r: #Restart ke menu
                                self.state = "MENU"
                                self.screen = pygame.display.set_mode((400, 300))
                    
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    game = MinesweeperGame()
    game.run()

