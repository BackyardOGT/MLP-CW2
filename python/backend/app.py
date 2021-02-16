from flask import Flask, request
from onitama.game import PvP, PvBot, BotVsBot
from onitama.rl import RandomAgent, SimpleAgent, RLAgent, MaskedCNNPolicy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

seed = 12442

twoPlayer = PvP(seed)
againstBot = PvBot(SimpleAgent(seed), seed)
# botVsBot = BotVsBot(RLAgent(seed, "../onitama-py/onitama/rl/logs/best_model.zip", thisPlayer=1),
#                     SimpleAgent(seed),
#                     seed)
botVsBot = BotVsBot(RandomAgent(seed, isPlayer1=True),
                    RLAgent(seed, "../onitama-py/onitama/rl/logs/best_model.zip", thisPlayer=2),
                    seed)
game = botVsBot
games = [twoPlayer, againstBot, botVsBot]
game_id = 2


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
