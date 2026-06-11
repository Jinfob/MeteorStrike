import pygame, sys
import game, homescreen, database

pygame.init()

running = True
launch_game = False
quit = False

streak = 0
current_streak = 0 
streak_max = 0

current_mode = "one_player"
while running:
    streak = 0
    current_streak = 0
    # MODE 1 JOUEUR
    if current_mode == "one_player":
        # SI DEJA CONNECTE
        if database.player1 is not None:
            launch_game, quit, current_mode, username = homescreen.homescreen_1p(database.player1["username"])
        else:
            launch_game, quit, current_mode, username = homescreen.homescreen_1p()
        if username and launch_game:
            database.connect_player(username)
    if current_mode == "two_player":
        if database.player1["username"] and database.player2["username"]:
            launch_game, quit, current_mode, username1, username2 = homescreen.homescreen_2p(database.player1["username"], database.player2["username"])
        elif database.player1["username"]:
            launch_game, quit, current_mode, username1, username2 = homescreen.homescreen_2p(database.player1["username"])
        else:
            launch_game, quit, current_mode, username1, username2 = homescreen.homescreen_2p()
        if username1 and username2 and launch_game:
            database.connect_player(username1)
            database.connect_player(username2, 2)
    niveau = 1
    while launch_game:
        if current_mode == "one_player":
            niveau_add, launch_game, streak, current_streak, streak_max = game.one_player(niveau, streak, current_streak, streak_max)
        if current_mode == "two_player":
            niveau_add, launch_game = game.two_player(niveau)
        niveau += niveau_add
    if database.player1["streak_max"] < streak_max:
        database.player1["streak_max"] = streak_max
    if database.player1["username"] and current_mode == "one_player":
        database.update_stats(database.player1, database.player1["streak_max"], database.player1["level_max_solo"], database.player1["game_played_solo"], database.player1["round_finished_solo"] - 1, database.player1["game_played_duo"], database.player1["round_played_duo"], database.player1["two_players_win"],database.player1["level_max_duo"])
    if database.player2["username"] and current_mode == "two_player":
        database.update_stats(database.player1, database.player1["streak_max"], database.player1["level_max_solo"], database.player1["game_played_solo"], database.player1["round_finished_solo"], database.player1["game_played_duo"], database.player1["round_played_duo"], database.player1["two_players_win"], database.player1["level_max_duo"])
        database.update_stats(database.player2, database.player2["streak_max"], database.player2["level_max_solo"], database.player2["game_played_solo"], database.player2["round_finished_solo"], database.player2["game_played_duo"], database.player2["round_played_duo"], database.player2["two_players_win"], database.player2["level_max_duo"])
    if quit:
        running = False
pygame.quit()
sys.exit()