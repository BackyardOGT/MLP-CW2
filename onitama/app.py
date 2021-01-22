from flask import Flask, request
from game import Game
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

game = Game()


@app.route('/getState')
def get_current_state():
    return game.get()


@app.route('/sendMove', methods=['GET', 'POST'])
def handle_move():
    data = request.json
    return game.step(data)


@app.route('/reset')
def reset():
    game.reset()
    return game.get()
