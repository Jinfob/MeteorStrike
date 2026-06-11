import pygame, random, math, time
from pathlib import Path
import database

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Game")
width, height = screen.get_size()
clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)

base_path = Path(__file__).resolve().parent.parent

life = 3

def get_difficulty(niveau):
    scale = math.log(niveau + 1) * 3.5

    speed_min = round(3 + scale)
    speed_max = round(6 + scale * 2)

    # Spawn : au niveau 1 ~8% de chance, au niveau 10 ~55%, au niveau 20 ~75%
    spawn_chance = min(8 + round(scale * 7), 80)

    # Max obstacles à l'écran : 3 au départ, 25 vers le niveau 10, 40 vers le niveau 20
    max_obstacles = min(3 + round(scale * 3.5), 50)

    return {
        "speed_min": speed_min,
        "speed_max": speed_max,
        "spawn_chance": spawn_chance,
        "max_obstacles": max_obstacles,
    }

meteor_img = pygame.image.load(base_path / "images" / "meteor.png").convert_alpha()
player_1_img = {'f' : pygame.image.load(base_path / "images" / "players" / "player_1" / "front.png").convert_alpha(),
              'r0' : pygame.image.load(base_path / "images" / "players" / "player_1" / "right0.png").convert_alpha(),
              'r1': pygame.image.load(base_path / "images" / "players" / "player_1" / "right1.png").convert_alpha(),
              'r2' : pygame.image.load(base_path / "images" / "players" / "player_1" / "right2.png").convert_alpha(),
              'l0': pygame.image.load(base_path / "images" / "players" / "player_1" / "left0.png").convert_alpha(),
              'l1' : pygame.image.load(base_path / "images" / "players" / "player_1" / "left1.png").convert_alpha(),
              'l2' : pygame.image.load(base_path / "images" / "players" / "player_1" / "left2.png").convert_alpha()
              }

player_2_img = {'f' : pygame.image.load(base_path / "images" / "players" / "player_2" / "front.png").convert_alpha(),
              'r0' : pygame.image.load(base_path / "images" / "players" / "player_2" / "right0.png").convert_alpha(),
              'r1': pygame.image.load(base_path / "images" / "players" / "player_2" / "right1.png").convert_alpha(),
              'r2' : pygame.image.load(base_path / "images" / "players" / "player_2" / "right2.png").convert_alpha(),
              'l0': pygame.image.load(base_path / "images" / "players" / "player_2" / "left0.png").convert_alpha(),
              'l1' : pygame.image.load(base_path / "images" / "players" / "player_2" / "left1.png").convert_alpha(),
              'l2' : pygame.image.load(base_path / "images" / "players" / "player_2" / "left2.png").convert_alpha()
              }

heart_img = {"h0" : pygame.image.load(base_path / "images" / "Icons" / "heart" /  "heart0.png").convert_alpha(),
             "h1" : pygame.image.load(base_path / "images" / "Icons" / "heart" / "heart1.png").convert_alpha(),
             "h2" : pygame.image.load(base_path / "images" / "Icons" / "heart" / "heart2.png").convert_alpha(),
             "h3" : pygame.image.load(base_path / "images" / "Icons" / "heart" / "heart3.png").convert_alpha(),
             }


game_background = pygame.image.load(base_path / "images" / "background" / "game_background.png").convert_alpha()
game_background = pygame.transform.scale(game_background, (width, height))


icon_timer = pygame.image.load(base_path / "images" / "Icons" / "clock.png").convert_alpha()
icon_level = pygame.image.load(base_path / "images" / "Icons" / "flag.png").convert_alpha()
icon_life  = heart_img["h3"]

def life_icon(life, full_life):
    full_life_split = full_life / 3
    if full_life_split * 2 < life <= full_life:
        icon_life = heart_img["h3"]
        icon_life  = pygame.transform.scale(icon_life, ICON_SIZE)
        return icon_life
    elif full_life_split < life <= full_life_split * 2:
        icon_life = heart_img["h2"]
        icon_life  = pygame.transform.scale(icon_life, ICON_SIZE)
        return icon_life
    elif life > 0:
        icon_life = heart_img["h1"]
        icon_life  = pygame.transform.scale(icon_life, ICON_SIZE)
        return icon_life
    else:
        icon_life = heart_img["h0"]
        icon_life  = pygame.transform.scale(icon_life, ICON_SIZE)
        return icon_life
    
ICON_SIZE = (32, 32)
icon_timer = pygame.transform.scale(icon_timer, ICON_SIZE)
icon_level = pygame.transform.scale(icon_level, ICON_SIZE)
icon_life  = pygame.transform.scale(icon_life, ICON_SIZE)

def draw_info_card_1p(joueur, surface, icon, label, x, y, card_w=90, card_h=50):
    pygame.draw.rect(surface, (0, 0, 0), (x, y, card_w, card_h), border_radius=8)
    pygame.draw.rect(surface, (80, 80, 80), (x, y, card_w, card_h), width=1, border_radius=8)
    icon_y = y + (card_h - icon.get_height()) // 2
    surface.blit(icon, (x + 8, icon_y))
    text_surf = font.render(label, True, (255, 255, 255))
    surface.blit(text_surf, (x + 8 + icon.get_width() + 8, y + (card_h - text_surf.get_height()) // 2))
    
def draw_info_card_2p(surface, icon, label, x, y, card_w=90, card_h=50):
    pygame.draw.rect(surface, (0, 0, 0), (x, y, card_w, card_h), border_radius=8)
    pygame.draw.rect(surface, (80, 80, 80), (x, y, card_w, card_h), width=1, border_radius=8)
    icon_y = y + (card_h - icon.get_height()) // 2
    surface.blit(icon, (x + 8, icon_y))
    text_surf = font.render(label, True, (255, 255, 255))
    surface.blit(text_surf, (x + 8 + icon.get_width() + 8, y + (card_h - text_surf.get_height()) // 2))
    
def update_infos(player, streak, niveau, mode, win=False):
    # définit si joueur 1 ou 2
    if player == 1:
        player = database.player1
    else:
        player = database.player2
    
    # Si mode 1 joueur
    if mode == "one_player":
        player["game_played_solo"] += 1
        player["round_finished_solo"] += niveau
        if player["level_max_solo"] < niveau -1:
            player["level_max_solo"] = niveau - 1
        if player["streak_max"] < streak:
            player["streak_max"] = streak
    
    # Si mode 2 joueur
    else:
        player["game_played_duo"] += 1
        player["round_played_duo"] += niveau
        if player["level_max_duo"] < niveau -1:
            player["level_max_duo"] = niveau - 1
        if win:
            player["two_players_win"] += 1

    


def one_player(niveau, streak, current_streak, streak_max):
        pygame.mouse.set_visible(False)
    
        
        class Player():
            def __init__(self, niveau, life, streak, current_streak, streak_max, px=width / 2, py=height, size=100, speed=10):
                self.niveau = niveau - 1
                if not (size - (10 * self.niveau)) <= 30:
                    self.size = size - (10 * self.niveau)
                else:
                    self.size = 30
                self.x = px
                self.y = py - self.size - 90
                self.speed = speed
                self.color = (0, 0, 0)
                self.full_life = life
                self.life = self.full_life
                self.streak_max = streak_max
                self.streak = current_streak + 1 if streak else 0
                self.streak_max = self.streak if self.streak > self.streak_max else streak_max
                self.var_left = 0
                self.var_right = 0
                self.image = pygame.transform.scale(player_1_img['f'], (self.size, self.size))
                self.mask = pygame.mask.from_surface(self.image)

            def move(self, keys):
                screen.blit(self.image, (self.x, self.y))
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    if not self.x == width - self.size:
                        self.x += self.speed
                        
                        #changement d'image pour l'animation
                        if self.var_right == 15:
                            self.var_right = 0
                        if self.var_right < 5:
                            num = 0
                        elif self.var_right < 10:
                            num = 1
                        elif self.var_right <= 15:
                            num = 2
                        image_l = 'r' + str(num)
                        self.image =pygame.transform.scale(player_1_img[image_l], (self.size, self.size))
                        self.mask = pygame.mask.from_surface(self.image)
                        self.var_right += 1
                    if self.x > width - self.size:
                        self.x = width - self.size
                elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
                    if not self.x == 0:
                        self.x -= self.speed
                        
                        #changement d'image pour l'animation
                        if self.var_left == 15:
                            self.var_left = 0
                        if self.var_left < 5:
                            num = 0
                        elif self.var_left < 10:
                            num = 1
                        elif self.var_left <= 15:
                            num = 2
                        image_l = 'l' + str(num)
                        self.image =pygame.transform.scale(player_1_img[image_l], (self.size, self.size))
                        self.mask = pygame.mask.from_surface(self.image)
                        self.var_left += 1
                    if self.x < 0:
                        self.x = 0
                else:
                    self.image = pygame.transform.scale(player_1_img['f'], (self.size, self.size))
                    self.mask = pygame.mask.from_surface(self.image)

            def collision(self):
                overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 120))
                self.image.blit(overlay, (0, 0))
                if self.life > 1:
                    self.life -= 1
                else:
                    self.life = 0
                    return False

            def update_level(self):
                if not self.size <= 30:
                    self.size -= 10
                else:
                    self.size = 30
                self.y = height - self.size


        class Obstacle():
            def __init__(self, index, niveau):
                self.niveau = niveau
                diff = get_difficulty(self.niveau)
                if self.niveau >= 10:
                    self.var = 10
                else:
                    self.var = self.niveau
                self.x = random.randint(0, width)
                self.size = random.randint(10, max(10, 10 * self.var))
                self.y = -self.size
                self.speed = random.randint(diff["speed_min"], diff["speed_max"])
                self.color = (255, 0, 0)
                self.index = index
                self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
                
                self.image = pygame.transform.scale(meteor_img, (self.size, self.size))
                self.mask = pygame.mask.from_surface(self.image)

            def move(self):
                self.y += self.speed
                self.rect.y = self.y
                screen.blit(self.image, self.rect)


        player = Player(niveau, life, streak, current_streak, streak_max)
        preobstacles = []
        obstacles = []
        for i in range(niveau * 10):
            if len(preobstacles) < 100:
                preobstacles.append(Obstacle(i, niveau))
        start_time = pygame.time.get_ticks()
        duration = 11 * 1000
        game = True

        while game:
            win = False
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = max(0, (duration - elapsed_time) // 1000)
            keys = pygame.key.get_pressed()
            screen.blit(game_background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game = False

                    if event.key == pygame.K_w:
                        win = True
                        game = False

            diff = get_difficulty(niveau)
            randobstacle = random.randint(0, 100)
            if randobstacle < diff["spawn_chance"]:
                if len(preobstacles) > 0 and len(obstacles) < diff["max_obstacles"]:
                    obstacles.append(preobstacles.pop())

            player.move(keys)
            for obstacle in obstacles[:]:
                obstacle.move()
                for obs in obstacles[:]:
                    if obs is not obstacle:
                        offset = (int(obs.rect.x - obstacle.rect.x), int(obs.rect.y - obstacle.rect.y))
                        if obstacle.mask.overlap(obs.mask, offset) and obstacle.speed == obs.speed and obstacle.y == 0 and obs.y == 0:
                            obstacles.remove(obstacle)
                            preobstacles.append(Obstacle(len(preobstacles), niveau))
                            break
                if obstacle.y > height:
                    obstacles.remove(obstacle)
                    preobstacles.append(Obstacle(len(preobstacles), niveau))
                offset = (int(obstacle.rect.x - player.x), int(obstacle.rect.y - player.y))
                if player.mask.overlap(obstacle.mask, offset):
                    etat = player.collision()
                    if etat == False:
                        game = False
                    obstacles.remove(obstacle)
                    if len(preobstacles) < (niveau * 10):
                        preobstacles.append(Obstacle(len(preobstacles), niveau))
                if remaining_time <= 0:
                    win = True
                    game = False
            
            icon_life = life_icon(player.life, player.full_life)
            draw_info_card_1p(1, screen, icon_level, f"{niveau}", 10, 10)
            draw_info_card_1p(1, screen, icon_timer, f"{remaining_time}", 100, 10)
            draw_info_card_1p(1, screen, icon_life,  f"{player.life}",   190, 10)
            pygame.display.flip()
            clock.tick(60)

        if not win:
            update_infos(1, 0, niveau, "one_player")
            end_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(end_text, (width / 2 - 80, height / 2))
            pygame.display.flip()
            pygame.event.get().clear()
            time.sleep(1)
            game = False
            return 0, False, False, player.streak, player.streak_max
        else:
            end_text = font.render(f"Level {niveau} completed", True, (0, 0, 255))
            screen.blit(end_text, (width / 2 - 80, height / 2))
            pygame.display.flip()
            pygame.event.get().clear()
            time.sleep(3)
            niveau += 1
            player.update_level()
            if player.life == player.full_life:
                return 1, True, True, player.streak, player.streak_max
            else:
                return 1, True, False, player.streak, player.streak_max
        
        
### MODE 2 JOUEURS 

def two_player(niveau):
        pygame.mouse.set_visible(False)
    
        
        class Player():
            def __init__(self, niveau, joueur, life, px=width / 2, py=height, size=100, speed=10):
                self.niveau = niveau - 1
                if not (size - (10 * self.niveau)) <= 30:
                    self.size = size - (10 * self.niveau)
                else:
                    self.size = 30
                self.joueur = joueur
                if self.joueur == 1:
                    self.image_joueur = player_1_img
                    self.x = px + 250
                else:
                    self.image_joueur = player_2_img
                    self.x = px - 250 - self.size
                self.y = py - self.size - 90
                self.speed = speed
                self.color = (0, 0, 0)
                self.full_life = life
                self.life = self.full_life
                self.var_left = 0
                self.var_right = 0
                self.image = pygame.transform.scale(self.image_joueur['f'], (self.size, self.size))
                self.mask = pygame.mask.from_surface(self.image)

            def move(self, keys):
                screen.blit(self.image, (self.x, self.y))
                if self.joueur == 1:
                    if keys[pygame.K_RIGHT]:
                        if not self.x == width - self.size:
                            self.x += self.speed
                            
                            #changement d'image pour l'animation
                            if self.var_right == 15:
                                self.var_right = 0
                            if self.var_right < 5:
                                num = 0
                            elif self.var_right < 10:
                                num = 1
                            elif self.var_right <= 15:
                                num = 2
                            image_l = 'r' + str(num)
                            self.image =pygame.transform.scale(self.image_joueur[image_l], (self.size, self.size))
                            self.mask = pygame.mask.from_surface(self.image)
                            self.var_right += 1
                        if self.x > width - self.size:
                            self.x = width - self.size
                    elif keys[pygame.K_LEFT]:
                        if not self.x == 0:
                            self.x -= self.speed
                            
                            #changement d'image pour l'animation
                            if self.var_left == 15:
                                self.var_left = 0
                            if self.var_left < 5:
                                num = 0
                            elif self.var_left < 10:
                                num = 1
                            elif self.var_left <= 15:
                                num = 2
                            image_l = 'l' + str(num)
                            self.image =pygame.transform.scale(self.image_joueur[image_l], (self.size, self.size))
                            self.mask = pygame.mask.from_surface(self.image)
                            self.var_left += 1
                        if self.x < 0:
                            self.x = 0
                    else:
                        self.image = pygame.transform.scale(self.image_joueur['f'], (self.size, self.size))
                        self.mask = pygame.mask.from_surface(self.image)
                        
                if self.joueur == 2:
                    if keys[pygame.K_d]:
                        if not self.x == width - self.size:
                            self.x += self.speed
                            
                            #changement d'image pour l'animation
                            if self.var_right == 15:
                                self.var_right = 0
                            if self.var_right < 5:
                                num = 0
                            elif self.var_right < 10:
                                num = 1
                            elif self.var_right <= 15:
                                num = 2
                            image_l = 'r' + str(num)
                            self.image =pygame.transform.scale(self.image_joueur[image_l], (self.size, self.size))
                            self.mask = pygame.mask.from_surface(self.image)
                            self.var_right += 1
                        if self.x > width - self.size:
                            self.x = width - self.size
                    elif keys[pygame.K_q]:
                        if not self.x == 0:
                            self.x -= self.speed
                            
                            #changement d'image pour l'animation
                            if self.var_left == 15:
                                self.var_left = 0
                            if self.var_left < 5:
                                num = 0
                            elif self.var_left < 10:
                                num = 1
                            elif self.var_left <= 15:
                                num = 2
                            image_l = 'l' + str(num)
                            self.image =pygame.transform.scale(self.image_joueur[image_l], (self.size, self.size))
                            self.mask = pygame.mask.from_surface(self.image)
                            self.var_left += 1
                        if self.x < 0:
                            self.x = 0
                    else:
                        self.image = pygame.transform.scale(self.image_joueur['f'], (self.size, self.size))
                        self.mask = pygame.mask.from_surface(self.image)

            def collision(self):
                overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 120))
                self.image.blit(overlay, (0, 0))
                if self.life > 1:
                    self.life -= 1
                else:
                    self.life = 0
                    return False

            def update_level(self):
                if not self.size <= 30:
                    self.size -= 10
                else:
                    self.size = 30
                self.y = height - self.size


        class Obstacle():
            def __init__(self, index, niveau):
                self.niveau = niveau
                diff = get_difficulty(self.niveau)
                if self.niveau >= 10:
                    self.var = 10
                else:
                    self.var = self.niveau
                self.x = random.randint(0, width)
                self.size = random.randint(10, max(10, 10 * self.var))
                self.y = -self.size
                self.speed = random.randint(diff["speed_min"], diff["speed_max"])
                self.color = (255, 0, 0)
                self.index = index
                self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
                
                self.image = pygame.transform.scale(meteor_img, (self.size, self.size))
                self.mask = pygame.mask.from_surface(self.image)

            def move(self):
                self.y += self.speed
                self.rect.y = self.y
                screen.blit(self.image, self.rect)


        player1 = Player(niveau, 1, life)
        player2 = Player(niveau, 2, life)

        preobstacles = []
        obstacles = []
        for i in range(niveau * 10):
            if len(preobstacles) < 100:
                preobstacles.append(Obstacle(i, niveau))
        start_time = pygame.time.get_ticks()
        duration = 11 * 1000
        game = True
        player1_loose = False
        player2_loose = False

        while game:
            win = False
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = max(0, (duration - elapsed_time) // 1000)
            keys = pygame.key.get_pressed()
            screen.blit(game_background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game = False

                    if event.key == pygame.K_w:
                        win = True
                        game = False

            diff = get_difficulty(niveau)
            randobstacle = random.randint(0, 100)
            if randobstacle < diff["spawn_chance"]:
                if len(preobstacles) > 0 and len(obstacles) < diff["max_obstacles"]:
                    obstacles.append(preobstacles.pop())

            player1.move(keys)
            player2.move(keys)
            for obstacle in obstacles[:]:
                obstacle.move()
                if obstacle.y > height:
                    obstacles.remove(obstacle)
                    preobstacles.append(Obstacle(len(preobstacles), niveau))
                offset_p1 = (int(obstacle.rect.x - player1.x), int(obstacle.rect.y - player1.y))
                offset_p2 = (int(obstacle.rect.x - player2.x), int(obstacle.rect.y - player2.y))
                if player1.mask.overlap(obstacle.mask, offset_p1):
                    etat = player1.collision()
                    if etat == False:
                        player1_loose = True
                        game = False
                    obstacles.remove(obstacle)
                    if len(preobstacles) < (niveau * 10):
                        preobstacles.append(Obstacle(len(preobstacles), niveau))
                if player2.mask.overlap(obstacle.mask, offset_p2):
                    etat = player2.collision()
                    if etat == False:
                        player2_loose = True
                        game = False
                    obstacles.remove(obstacle)
                    if len(preobstacles) < (niveau * 10):
                        preobstacles.append(Obstacle(len(preobstacles), niveau))
                if remaining_time <= 0:
                    win = True
                    game = False
            
            icon_life_p1 = life_icon(player1.life, player1.full_life)
            icon_life_p2 = life_icon(player2.life, player2.full_life)
            card_w, card_h = 90, 50
            gap = 10
            # Temps + Niveau centrés en haut
            total_w = card_w * 2 + gap
            center_x = width // 2 - total_w // 2
            draw_info_card_2p(screen, icon_timer, f"{remaining_time}", center_x, 10, card_w, card_h)
            draw_info_card_2p(screen, icon_level, f"{niveau}", center_x + card_w + gap, 10, card_w, card_h)
            draw_info_card_2p(screen, icon_life_p1, f"{player1.life}", width - card_w - 10, 10, card_w, card_h)
            draw_info_card_2p(screen, icon_life_p2, f"{player2.life}", 10 , 10, card_w, card_h)
            pygame.display.flip()
            clock.tick(60)

        if not win:
            if player1_loose and player2_loose:
                end_text = font.render("Draw!", True, (255, 255, 0))
                update_infos(1, 0, niveau, "two_player")
                update_infos(2, 0, niveau, "two_player")
            elif player1_loose:
                end_text = font.render("Player 2 Wins!", True, (0, 255, 0))
                update_infos(1, 0, niveau, "two_player")
                update_infos(2, 0, niveau, "two_player", win=True)
            else:
                end_text = font.render("Player 1 Wins!", True, (255, 0, 0))
                update_infos(1, 0, niveau, "two_player", win=True)
                update_infos(2, 0, niveau, "two_player")
            screen.blit(end_text, (width / 2 - 80, height / 2))
            pygame.display.flip()
            pygame.event.get().clear()
            time.sleep(1)
            game = False
            return 0, False
        else:
            end_text = font.render(f"Level {niveau} completed", True, (0, 0, 255))
            screen.blit(end_text, (width / 2 - 80, height / 2))
            pygame.display.flip()
            time.sleep(3)
            niveau += 1
            player1.update_level()
            player2.update_level()
            return 1, True