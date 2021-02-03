from flask import Flask, request
from onitama.game import PvP, PvBot, BotVsBot
from onitama.rl import RandomAgent, SimpleAgent
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

twoPlayer = PvP()
againstBot = PvBot(SimpleAgent())
botVsBot = BotVsBot(RandomAgent(isPlayer1=True), SimpleAgent())
game = twoPlayer
games = [twoPlayer, againstBot, botVsBot]
game_id = 0


@app.route('/getState')
def get_current_state():
    return game.get()


@app.route('/sendMove', methods=['GET', 'POST'])
def handle_move():
    data = request.json
    return game.stepApi(data)


@app.route('/stepBot')
def step_bot():
    return game.stepBot()


@app.route('/reset')
def reset():
    game.reset()
    return game.get()


@app.route('/toggleGameMode')
def toggle_game_mode():
    global game, games, game_id
    # swtich
    game_id = (game_id + 1) % len(games)
    game = games[game_id]
    return game.get()
