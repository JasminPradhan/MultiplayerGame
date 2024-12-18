import pygame
from network import Network
import pickle
pygame.init()
pygame.font.init()

width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")


class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", 40)
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def redrawWindow(win, game, p):
    win.fill((243,126,111))

    leaderboard_bg_color = (50, 50, 50)  # Dark gray background for leaderboard
    leaderboard_text_color = (255, 255, 255)  # White text color
    border_color = (200, 200, 200)  # Light gray border
    leaderboard_x = 50
    leaderboard_y = 10
    leaderboard_width = width - 100
    leaderboard_height = 120
    font_size = 24  # Smaller font for leaderboard

    # Draw leaderboard background with border
    pygame.draw.rect(win, border_color,
                     (leaderboard_x - 2, leaderboard_y - 2, leaderboard_width + 4, leaderboard_height + 4))
    pygame.draw.rect(win, leaderboard_bg_color, (leaderboard_x, leaderboard_y, leaderboard_width, leaderboard_height))

    # Title for the leaderboard
    font = pygame.font.SysFont("comicsans", 28, bold=True)
    title_text = font.render("Leaderboard", True, leaderboard_text_color)
    win.blit(title_text, (leaderboard_x + leaderboard_width // 2 - title_text.get_width() // 2, leaderboard_y + 5))

    # Display leaderboard entries
    font = pygame.font.SysFont("comicsans", font_size)
    for i, (player, stats) in enumerate(game.leaderboard):
        player_text = f"{i + 1}. {player} - Streak: {stats['streak']}"
        text = font.render(player_text, True, leaderboard_text_color)
        win.blit(text, (leaderboard_x + 10, leaderboard_y + 35 + i * (font_size + 5)))

    # Game state rendering

    if not(game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Waiting for Player...", 1, (255,0,0), True)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
    else:
        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Your Move", 1, (0, 255,255))
        win.blit(text, (80, 200))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 200))

        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.bothMoved():
            text1 = font.render(move1, 1, (0,0,0))
            text2 = font.render(move2, 1, (0, 0, 0))
        else:
            if game.p1Move and p == 0:
                text1 = font.render(move1, 1, (0,0,0))
            elif game.p1Move:
                text1 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text1 = font.render("Waiting...", 1, (0, 0, 0))

            if game.p2Move and p == 1:
                text2 = font.render(move2, 1, (0,0,0))
            elif game.p2Move:
                text2 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text2 = font.render("Waiting...", 1, (0, 0, 0))

        if p == 1:
            win.blit(text2, (100, 350))
            win.blit(text1, (400, 350))
        else:
            win.blit(text1, (100, 350))
            win.blit(text2, (400, 350))

        for btn in btns:
            btn.draw(win)

    pygame.display.update()


btns = [Button("Rock", 50, 500, (0,0,0)), Button("Scissors", 250, 500, (255,0,0)), Button("Paper", 450, 500, (0,255,0))]

def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("You are player", player)

    while run:
        clock.tick(60)
        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break

        if game.bothMoved():
            redrawWindow(win, game, player)
            pygame.time.delay(500)
            try:
                game = n.send("reset")
            except:
                run = False
                print("Couldn't get game")
                break

            font = pygame.font.SysFont("comicsans", 90)
            if (game.win() == 1 and player == 1) or (game.win() == 0 and player == 0):
                text = font.render("You Won!", 1, (255,0,0))
            elif game.win() == -1:
                text = font.render("Tie Game!", 1, (255,0,0))
            else:
                text = font.render("You Lost...", 1, (255, 0, 0))

            win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(2000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Move:
                                print(btn.text)
                                n.send(btn.text)
                        else:
                            if not game.p2Move:
                                print(btn.text)
                                n.send(btn.text)

        redrawWindow(win, game, player)

def menu_screen():
    run = True
    clock = pygame.time.Clock()
    player_name = ""

    while run:
        clock.tick(60)
        win.fill((243,126,111))


        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Click to Play!", 1, (255,0,0))
        win.blit(text, (100,200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()

while True:
    menu_screen()
