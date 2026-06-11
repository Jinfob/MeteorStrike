import pygame
from pathlib import Path
import database

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Game")
width, height = screen.get_size()
font = pygame.font.Font(None, 50)
body_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 80)
placeholder_font = pygame.font.Font(None, 60)

base_path = Path(__file__).resolve().parent.parent


player_1_img = pygame.image.load(base_path / "images" / "players" / "player_1" / "front.png").convert_alpha()
player_2_img = pygame.image.load(base_path / "images" / "players" / "player_2" / "front.png").convert_alpha()


homescreen_background = pygame.image.load(base_path / "images" / "background" / "homescreen_background.png").convert_alpha()
homescreen_background = pygame.transform.scale(homescreen_background, (width, height))

icon_1p = pygame.image.load(base_path / "images" / "icons" / "game_mode" / "icon_1p.png").convert_alpha()
icon_2p = pygame.image.load(base_path / "images" / "icons" / "game_mode" / "icon_2p.png").convert_alpha()

def loading(screen, width, height):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((128, 128, 128, 150))
    loading_text = font.render("Loading...", True, (255, 255, 255))
    loading_text_rect = loading_text.get_rect(center=(width//2, height//2))
    screen.blit(overlay, (0, 0))
    screen.blit(loading_text, loading_text_rect)
    pygame.display.flip()

class InputBox:
    def __init__(self, x, y, width, height, font, player, username = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder_font.render(f"Player {player} Username", True, (100, 100, 100))
        self.font = font
        self.username = "" if username is None else username
        self.text = "" if not self.username else self.username
        self.active = False
        self.COLOR_INACTIVE = (150, 150, 150)
        self.COLOR_ACTIVE   = (255, 255, 255)

    def validate(self):
        self.username = self.text
        self.active = False

    def handle_event(self, event, button_start=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.validate() 
                self.active = False
            if button_start and button_start.collidepoint(event.pos):
                self.validate()

        if event.type == pygame.KEYDOWN and self.active:
            if len(self.text) <= 11 or event.key in (pygame.K_BACKSPACE, pygame.K_RETURN):
                if event.key == pygame.K_RETURN:
                    self.validate()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        border = 3 if self.active else 1
        pygame.draw.rect(screen, (0, 0, 0), self.rect, border)
        surface = self.font.render(self.text, True, (0, 0, 0))
        text_y = self.rect.y + (self.rect.height - surface.get_height()) // 2
        text_x = self.rect.x + (self.rect.width - surface.get_width()) // 2
        screen.blit(surface, (text_x, text_y))
        if not self.active and self.username == "":
            screen.blit(self.placeholder, (text_x - 190, text_y))

def leaderboard(mode="solo"):
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    run_leaderboard = True
    leaderboard_w = 700
    leaderboard_h = height - 150
    leaderboard_x = width / 2 - (leaderboard_w / 2)
    leaderboard_y = height / 2 - (leaderboard_h / 2)
    fond = pygame.Rect(leaderboard_x, leaderboard_y, leaderboard_w, leaderboard_h)
    leaderboard_solo = pygame.image.load(base_path / "images" / "leaderboard_solo.png")
    leaderboard_solo = pygame.transform.scale(leaderboard_solo, (leaderboard_w, leaderboard_h))
    leaderboard_duo = pygame.image.load(base_path / "images" / "leaderboard_duo.png")
    leaderboard_duo = pygame.transform.scale(leaderboard_duo, (leaderboard_w, leaderboard_h))
    button_solo = pygame.Rect(leaderboard_x + ((0.5/100) * leaderboard_w), leaderboard_y + ((0.5/100) * leaderboard_h),leaderboard_w / 2 + 15, leaderboard_h * (16/100))
    button_duo = pygame.Rect(leaderboard_x + leaderboard_w / 2 - 15, leaderboard_y + ((0.5/100) * leaderboard_h),leaderboard_w / 2 + 10, leaderboard_h * (16/100))
    leaderboard_loading = True
    order_by = "streak_max"
    
    button_solo_username = pygame.Rect(472, 212, 171, 68)
    button_order1 = pygame.Rect(647, 212, 166, 68)
    button_order2 = pygame.Rect(817, 212, 167, 68)
    button_order3 = pygame.Rect(987, 212, 140, 68)
    
    slot_x = [471, 646, 816, 987]
    slot_w = [172, 167, 168, 140]
    slot_y = [284, 338, 390, 441, 492, 543, 594, 645, 695, 746]
    slot_h = [50, 47, 47, 47, 47, 47, 47, 46, 47, 50]
    slots = [
        [pygame.Rect(slot_x[col], slot_y[row], slot_w[col], slot_h[row]) for col in range(4)]
        for row in range(10)
    ]

    rendered_slots = []
    while run_leaderboard:
        text_solo = font.render("Solo", True, (255, 255, 255) if mode == "solo" else (210, 220, 255))
        text_solo_rect = text_solo.get_rect(center=button_solo.center)
        text_duo = font.render("Duo", True, (210, 220, 255) if mode == "duo" else (255, 255, 255))
        text_duo_rect = text_duo.get_rect(center=button_duo.center)
        screen.blit(homescreen_background, (0, 0))
        
        def select():
            pygame.draw.rect(screen, (80, 93, 171), button_order1) if order_by == "streak_max" or order_by == "two_players_win" else None
            pygame.draw.rect(screen, (80, 93, 171), button_order2) if order_by == "level_max_solo" or order_by == "level_max_duo" else None
            pygame.draw.rect(screen, (80, 93, 171), button_order3) if order_by == "game_played_solo" or order_by == "game_played_duo" else None

            
        screen.blit(leaderboard_solo, fond) if mode == "solo" else screen.blit(leaderboard_duo, fond)
        

        text_solo_username = body_font.render("Username", True, (255, 255, 255))
        text_solo_username_rect = text_solo_username.get_rect(center=button_solo_username.center)
        text_solo_streak = body_font.render("Streak", True, (255, 255, 255)) if mode == "solo" else body_font.render("Wins", True, (255, 255, 255))
        text_solo_streak_rect = text_solo_streak.get_rect(center=button_order1.center)
        text_solo_level = body_font.render("Level", True, (255, 255, 255)) if mode == "solo" else body_font.render("Level Max", True, (255, 255, 255))
        text_solo_level_rect = text_solo_level.get_rect(center=button_order2.center)
        text_solo_games = body_font.render("Games", True, (255, 255, 255))
        text_solo_games_rect = text_solo_games.get_rect(center=button_order3.center)

        select()
        
        screen.blit(text_solo_username, text_solo_username_rect)
        screen.blit(text_solo_streak, text_solo_streak_rect)
        screen.blit(text_solo_level, text_solo_level_rect)
        screen.blit(text_solo_games, text_solo_games_rect)
            
        screen.blit(text_solo, text_solo_rect)
        screen.blit(text_duo, text_duo_rect)
        
        if leaderboard_loading:
            loading(screen, width, height)
            leaderboard_data = database.load_leaderboard(order_by)
            leaderboard_loading = False

            keys = ["username", "streak_max", "level_max_solo", "game_played_solo"] if mode == "solo" \
                else ["username", "two_players_win", "level_max_duo", "game_played_duo"]

            rendered_slots = []
            for i, entry in enumerate(leaderboard_data):
                row_surfaces = []
                for j, key in enumerate(keys):
                    value = entry[key]
                    text = body_font.render(str(value) if value is not None else "-", True, (255, 255, 255))
                    rect = text.get_rect(center=slots[i][j].center)
                    row_surfaces.append((text, rect))
                rendered_slots.append(row_surfaces)

        for row in rendered_slots:
            for text, rect in row:
                screen.blit(text, rect)
            
        if screen.get_at(pygame.mouse.get_pos()) == (0, 14, 122) or button_order1.collidepoint(pygame.mouse.get_pos()) or button_order2.collidepoint(pygame.mouse.get_pos()) or button_order3.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run_leaderboard = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if screen.get_at(event.pos)[:3] == (0, 14, 122):
                    mode = "solo" if mode == "duo" else "duo"
                    if order_by == "streak_max":
                        order_by = "two_players_win"
                    elif order_by == "two_players_win":
                        order_by = "streak_max"
                    elif order_by == "level_max_solo":
                        order_by = "level_max_duo"
                    elif order_by == "level_max_duo":
                        order_by = "level_max_solo"
                    leaderboard_loading = True
                elif button_order1.collidepoint(event.pos) and not (order_by == "streak_max" or order_by == "two_players_win"):
                    order_by = "streak_max" if mode == "solo" else "two_players_win"
                    leaderboard_loading = True
                elif button_order2.collidepoint(event.pos) and not (order_by == "level_max_solo" or order_by == "level_max_duo"):
                    order_by = "level_max_solo" if mode == "solo" else "level_max_duo"
                    leaderboard_loading = True
                elif button_order3.collidepoint(event.pos) and not (order_by == "game_played_solo" or order_by == "game_played_duo"):
                    order_by = "game_played_solo" if mode == "solo" else "game_played_duo"
                    leaderboard_loading = True
        pygame.display.flip()



def homescreen_1p(player=None):
    launch_game = False; run_homescreen = True; quit = False
    current_mode = "one_player"
    pygame.mouse.set_visible(True)
    
    
    title = title_font.render("Meteor Strike", True, (255, 0, 0))
    
    button_width = 300; button_height = 100; button_spacing = 40
    
    fond = pygame.Rect(width / 2 - 300, 80, 600, height - 160)
    
    ### DEFINITION DES BOUTONS
    # Start 
    button_start = pygame.Rect(width / 2 - button_width / 2, fond.height - button_height * 3 - button_spacing * 2.5, button_width, button_height)
    text_start = font.render("Start", True, (255, 255, 255))
    text_start_rect = text_start.get_rect(center=button_start.center)
    
    # Leaderboard
    button_leaderboard = pygame.Rect(width / 2 - button_width / 2, fond.height - button_height * 2 - button_spacing * 2, button_width, button_height)
    text_leaderboard = font.render("Leaderboard", True, (255, 255, 255))
    text_leaderboard_rect = text_leaderboard.get_rect(center=button_leaderboard.center)
    
    # Exit
    button_exit = pygame.Rect(width / 2 - button_width / 2, fond.height - button_spacing, button_width, button_height)
    text_exit = font.render("Exit", True, (255, 255, 255))
    text_exit_rect = text_exit.get_rect(center=button_exit.center)
    
    # Mode selection (1P or 2P)
    icon_1p_scaled = pygame.transform.scale(icon_1p, (135, 75))
    icon_2p_scaled = pygame.transform.scale(icon_2p, (90, 50))
    button_1p_rect = pygame.Rect(10, 200, 135, 75)
    button_2p_rect = pygame.Rect(142, 212.5, 90, 50)
    button_1p_mask = pygame.mask.from_surface(icon_1p_scaled)
    button_2p_mask = pygame.mask.from_surface(icon_2p_scaled)
    text_1p = font.render("1P", True, (255, 255, 255))
    text_1p_rect = text_1p.get_rect(center=button_1p_rect.center)
    text_2p = font.render("2P", True, (255, 255, 255))
    text_2p_rect = text_2p.get_rect(center=button_2p_rect.center)

    if player:
        textbox = InputBox(width / 2 - 200, fond.height - button_height * 4 - button_spacing * 3, 400, 80, font, 1, player)
    else:
        textbox = InputBox(width / 2 - 200, fond.height - button_height * 4 - button_spacing * 3, 400, 80, font, 1)

    def is_hovering(mask, rect, pos):
        if not rect.collidepoint(pos):
            return False
        local_x = pos[0] - rect.x
        local_y = pos[1] - rect.y
        return bool(mask.get_at((local_x, local_y)))
    
    while run_homescreen:
        screen.blit(homescreen_background, (0, 0))
        screen.blit(pygame.transform.scale(player_1_img, (height * 0.5, height * 0.5)), (width - height * 0.5 - 10, height * 0.5))
        surface = pygame.Surface((fond.width, fond.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 150), pygame.Rect(0, 0, fond.width, fond.height), border_radius=10)
        screen.blit(surface, (fond.x, fond.y))
        screen.blit(title, (width / 2 - title.get_width() / 2, fond.y + 40))
        # boutons
        if (textbox.text or database.player1["username"]) and textbox.text:
            pygame.draw.rect(screen, (0, 150, 255), button_start, width=0, border_radius=8)
        else:
            pygame.draw.rect(screen, (40, 60, 90), button_start, width=0, border_radius=8)
        screen.blit(text_start, text_start_rect)
        pygame.draw.rect(screen, (0, 150, 255), button_leaderboard, width=0, border_radius=8)
        screen.blit(text_leaderboard, text_leaderboard_rect)
        pygame.draw.rect(screen, (0, 150, 255), button_exit, width=0, border_radius=8)
        screen.blit(text_exit, text_exit_rect)
        pygame.draw.rect(screen, (255, 255, 255), textbox, width=0, border_radius=8)
        textbox.draw(screen)
        screen.blit(icon_1p_scaled, button_1p_rect)
        screen.blit(text_1p, text_1p_rect)
        screen.blit(icon_2p_scaled, button_2p_rect)
        screen.blit(text_2p, text_2p_rect)
        pseudo_surface = font.render(textbox.username, True, (0, 0, 0))
        pseudo_rect = pseudo_surface.get_rect(center=textbox.rect.center)
        screen.blit(pseudo_surface, pseudo_rect) if not textbox.active else None
        mouse_pos = pygame.mouse.get_pos()
        if (button_start.collidepoint(mouse_pos) and textbox.text) or button_leaderboard.collidepoint(mouse_pos) or button_exit.collidepoint(mouse_pos) or is_hovering(button_1p_mask, button_1p_rect, mouse_pos) or is_hovering(button_2p_mask, button_2p_rect, mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif textbox.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.display.flip()
        for event in pygame.event.get():
            textbox.handle_event(event, button_start)
            if event.type == pygame.QUIT:
                launch_game = False
                quit = True
                run_homescreen = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_start.collidepoint(event.pos):
                    if textbox.username:
                        launch_game = True
                        quit = False
                        run_homescreen = False
                elif button_leaderboard.collidepoint(event.pos):
                    leaderboard("solo")
                elif button_exit.collidepoint(event.pos):
                    launch_game = False
                    quit = True
                    run_homescreen = False
                elif button_1p_rect.collidepoint(event.pos):
                    current_mode = "one_player"
                    launch_game = False
                    quit = False
                    run_homescreen = False
                elif button_2p_rect.collidepoint(event.pos):
                    current_mode = "two_player"
                    launch_game = False
                    quit = False
                    run_homescreen = False
        if launch_game:
            loading(screen, width, height)
    return launch_game, quit, current_mode, textbox.username

def homescreen_2p(player1=None, player2=None):
    launch_game = False; run_homescreen = True; quit = False
    current_mode = "two_player"
    pygame.mouse.set_visible(True)
    
    title = title_font.render("Meteor Strike", True, (255, 0, 0))
    
    button_width = 300; button_height = 100; button_spacing = 40
    
    fond = pygame.Rect(width / 2 - 300, 80, 600, height - 160)
    
    ### DEFINITION DES BOUTONS
    # Start 
    button_start = pygame.Rect(width / 2 - button_width / 2, fond.height - button_height * 3 - button_spacing * 2.5, button_width, button_height)
    text_start = font.render("Start", True, (255, 255, 255))
    text_start_rect = text_start.get_rect(center=button_start.center)
    
    # Leaderboard
    button_leaderboard = pygame.Rect(width / 2 - button_width / 2, fond.height - button_height * 2 - button_spacing * 2, button_width, button_height)
    text_leaderboard = font.render("Leaderboard", True, (255, 255, 255))
    text_leaderboard_rect = text_leaderboard.get_rect(center=button_leaderboard.center)
    
    # Exit
    button_exit = pygame.Rect(width / 2 - button_width / 2, fond.height - button_spacing, button_width, button_height)
    text_exit = font.render("Exit", True, (255, 255, 255))
    text_exit_rect = text_exit.get_rect(center=button_exit.center)
    
    # Mode selection (1P or 2P)
    icon_1p_scaled = pygame.transform.scale(icon_1p, (90, 50))
    icon_2p_scaled = pygame.transform.scale(icon_2p, (135, 75))
    button_1p_rect = pygame.Rect(10, 212.5, 90, 50)
    button_2p_rect = pygame.Rect(95, 200, 135, 75)
    button_1p_mask = pygame.mask.from_surface(icon_1p_scaled)
    button_2p_mask = pygame.mask.from_surface(icon_2p_scaled)
    text_1p = font.render("1P", True, (255, 255, 255))
    text_1p_rect = text_1p.get_rect(center=button_1p_rect.center)
    text_2p = font.render("2P", True, (255, 255, 255))
    text_2p_rect = text_2p.get_rect(center=button_2p_rect.center)

    if player1:
        textbox1 = InputBox(width / 2 - 200, height - fond.height + 40, 400, 55, font, 1, player1)
    else:
        textbox1 = InputBox(width / 2 - 200, height - fond.height + 40, 400, 55, font, 1)
    if player2:
        textbox2 = InputBox(width / 2 - 200, height - fond.height + 110, 400, 55, font, 2, player2)
    else:
        textbox2 = InputBox(width / 2 - 200, height - fond.height + 110, 400, 55, font, 2)

    def is_hovering(mask, rect, pos):
        if not rect.collidepoint(pos):
            return False
        local_x = pos[0] - rect.x
        local_y = pos[1] - rect.y
        return bool(mask.get_at((local_x, local_y)))
    
    while run_homescreen:
        screen.blit(homescreen_background, (0, 0))
        screen.blit(pygame.transform.scale(player_1_img, (height * 0.5, height * 0.5)), (width - height * 0.5 - 10, height * 0.5))
        screen.blit(pygame.transform.scale(player_2_img, (height * 0.5, height * 0.5)), (10, height * 0.5))
        surface = pygame.Surface((fond.width, fond.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 150), pygame.Rect(0, 0, fond.width, fond.height), border_radius=10)
        screen.blit(surface, (fond.x, fond.y))
        screen.blit(title, (width / 2 - title.get_width() / 2, fond.y + 40))
        # boutons
        if ((textbox1.text and textbox2.text) or (database.player1["username"] and database.player2["username"])) and (textbox1.text and textbox2.text):
            pygame.draw.rect(screen, (0, 150, 255), button_start, width=0, border_radius=8)
        else:
            pygame.draw.rect(screen, (40, 60, 90), button_start, width=0, border_radius=8)
        screen.blit(text_start, text_start_rect)
        pygame.draw.rect(screen, (0, 150, 255), button_leaderboard, width=0, border_radius=8)
        screen.blit(text_leaderboard, text_leaderboard_rect)
        pygame.draw.rect(screen, (0, 150, 255), button_exit, width=0, border_radius=8)
        screen.blit(text_exit, text_exit_rect)
        textbox1.draw(screen)
        textbox2.draw(screen)
        screen.blit(icon_1p_scaled, button_1p_rect)
        screen.blit(text_1p, text_1p_rect)
        screen.blit(icon_2p_scaled, button_2p_rect)
        screen.blit(text_2p, text_2p_rect)
        pseudo1_surface = font.render(textbox1.username, True, (0, 0, 0))
        pseudo1_rect = pseudo1_surface.get_rect(center=textbox1.rect.center)
        screen.blit(pseudo1_surface, pseudo1_rect) if not textbox1.active else None
        pseudo2_surface = font.render(textbox2.username, True, (0, 0, 0))
        pseudo2_rect = pseudo2_surface.get_rect(center=textbox2.rect.center)
        screen.blit(pseudo2_surface, pseudo2_rect) if not textbox2.active else None
        mouse_pos = pygame.mouse.get_pos()
        if (
            button_start.collidepoint(pygame.mouse.get_pos()) and ((textbox1.text and textbox2.text) or (database.player1["username"] and database.player2["username"]) )) or button_leaderboard.collidepoint(pygame.mouse.get_pos()) or button_exit.collidepoint(pygame.mouse.get_pos()) or is_hovering(button_1p_mask, button_1p_rect, mouse_pos) or is_hovering(button_2p_mask, button_2p_rect, mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif textbox1.rect.collidepoint(mouse_pos) or textbox2.rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.display.flip()
        for event in pygame.event.get():
            textbox1.handle_event(event)
            textbox2.handle_event(event)
            if event.type == pygame.QUIT:
                launch_game = False
                quit = True
                run_homescreen = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_start.collidepoint(event.pos):
                    if textbox1.username and textbox2.username:
                        launch_game = True
                        quit = False
                        run_homescreen = False
                elif button_leaderboard.collidepoint(event.pos):
                    leaderboard("duo")
                elif button_exit.collidepoint(event.pos):
                    launch_game = False
                    quit = True
                    run_homescreen = False
                elif button_1p_rect.collidepoint(event.pos):
                    current_mode = "one_player"
                    launch_game = False
                    quit = False
                    run_homescreen = False
                elif button_2p_rect.collidepoint(event.pos):
                    current_mode = "two_player"
                    launch_game = False
                    quit = False
                    run_homescreen = False
        if launch_game:
            loading(screen, width, height)
    return launch_game, quit, current_mode, textbox1.username, textbox2.username