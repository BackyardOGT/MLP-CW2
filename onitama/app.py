import time
from flask import Flask, request, jsonify
from board import Game
import json

app = Flask(__name__)

board = Game()


@app.route('/getState')
def get_current_state():
    return board.get()


@app.route('/sendMove', methods=['GET', 'POST'])
def handle_move():
    data = request.json
    return board.step(data)
