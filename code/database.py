import sqlite3
from datetime import datetime
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent

player1 = {
    "username": None,
    "streak_max": 0,
    "level_max_solo": 0,
    "game_played_solo": 0,
    "round_finished_solo": 0,
    "game_played_duo": 0,
    "round_played_duo": 0,
    "two_players_win": 0,
    "level_max_duo" : 0
}
player2 = {
    "username": None,
    "streak_max": 0,
    "level_max_solo": 0,
    "game_played_solo": 0,
    "round_finished_solo": 0,
    "game_played_duo": 0,
    "round_played_duo": 0,
    "two_players_win": 0,
    "level_max_duo" : 0
}


def get_db():
    con = sqlite3.connect(base_path / "data" / "meteorstrike.db")
    return con

def update_stats(player, streak_max, level_max_solo, game_played_solo, round_finished_solo, game_played_duo, round_played_duo, two_players_win, level_max_duo):
    with get_db() as con:
        cursor = con.cursor()
        cursor.execute("UPDATE Statistiques SET streak_max = ?, level_max_solo = ?, game_played_solo = ?, round_finished_solo = ?, game_played_duo = ?, round_played_duo = ?, two_players_win = ?, level_max_duo = ? WHERE username = ?",
                       (streak_max, level_max_solo, game_played_solo, round_finished_solo, game_played_duo, round_played_duo, two_players_win, level_max_duo, player["username"]))
        
def update_player(player):
    with get_db() as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT streak_max, level_max_solo, game_played_solo, round_finished_solo, game_played_duo, round_played_duo, two_players_win FROM Statistiques WHERE username = ?",
            (player["username"],)
        )
        stats = cursor.fetchone()
        if stats:
            player["streak_max"] = stats[0]
            player["level_max_solo"] = stats[1]
            player["game_played_solo"] = stats[2]
            player["round_finished_solo"] = stats[3]
            player["game_played_duo"] = stats[4]
            player["round_played_duo"] = stats[5]
            player["two_players_win"] = stats[6]

def connect_player(username, player=1):
    with get_db() as con:
        cursor = con.cursor()
        existe = cursor.execute(
            "SELECT username FROM Statistiques WHERE LOWER(username) = ?", (username.lower(),)
        ).fetchone()
        if not existe:
            cursor.execute(
                "INSERT INTO Statistiques (username, first_connection, last_connection) VALUES (?, ?, ?)",
                (username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            username_bdd = username
        else:
            cursor.execute(
                "UPDATE Statistiques SET last_connection = ? WHERE username = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), existe[0])
            )
            username_bdd = existe[0]

    p = player1 if player == 1 else player2
    p["username"] = username_bdd
    update_player(p)
    

    return username_bdd

def load_leaderboard(order_by="streak_max"):
    with get_db() as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT username, streak_max, level_max_solo, game_played_solo, round_finished_solo, game_played_duo, round_played_duo, two_players_win, level_max_duo FROM Statistiques ORDER BY {order_by} DESC")
        leaderboard_data = cursor.fetchall()
        leaderboard = [{"username": row[0], "streak_max": row[1], "level_max_solo": row[2], "game_played_solo": row[3], "round_finished_solo": row[4], "game_played_duo": row[5], "round_played_duo": row[6], "two_players_win": row[7], "level_max_duo": row[8]} for row in leaderboard_data]
        leaderboard = leaderboard[:10]
        empty = {
        "username": None,
        "streak_max": None,
        "level_max_solo": None,
        "game_played_solo": None,
        "round_finished_solo": None,
        "game_played_duo": None,
        "round_played_duo": None,
        "two_players_win": None,
        "level_max_duo": None
    }

    leaderboard = leaderboard[:10]
    while len(leaderboard) < 10:
        leaderboard.append(empty)
        print(leaderboard)
    return leaderboard