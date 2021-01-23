from flask import Flask, request
from game import PvP, VsBot
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

twoPlayer = PvP()
againstBot = VsBot()
game = twoPlayer
isTwoPlayer = True


@app.route('/getState')
def get_current_state():
    return game.get()


@app.route('/sendMove', methods=['GET', 'POST'])
def handle_move():
    data = request.json
    return game.stepApi(data)


@app.route('/reset')
def reset():
    game.reset()
    return game.get()


@app.route('/toggleGameMode')
def toggle_game_mode():
    global game, isTwoPlayer
    # swtich
    game = againstBot if isTwoPlayer else twoPlayer
    isTwoPlayer = not isTwoPlayer
    return game.get()
