
## Usage

```
git clone ....
cd MLP-CW2
```

#### Python

See above, then

Install the python library

```
cd python
pip install -e .
```

#### UI

See above, then

To use backed for browser, run flask

```
cd flask
flask run
```

Then open `react/build/index.html` in a browser.

## RL

Observations:
(5 x 5 x 59) of::
    (5 x 5 x 5) cards - 2 current and 1 next for each player
    (5 x 5 x 4) board - kings and pawns for each player
and
    (5 x 5 x 50) (50 = 25 (board) x 2 (cards)) mask of valid moves
Actions:
    (5 x 5 x 25 x 2) board spaces x number of moves x number cards - each filter is the probability of picking a piece
    from this board location, filter dimesnions are 25 (5 x 5) possible moves to move to.
    Mask by the mask obsercation from env.
    Flatten
    Softmax to get move
    Return a 1250 (2 x 5 x 5 x 25 flat) one hot action



## TODOs

#### Higher priority

* Heuristic agent see onitama.rl.agents.RandomAgent (need to define XXX.get_action())
* Reward see onitama.rl.env OnitamaEnv.get_reward()
* Masking for actions - masking allowing invalid moves - see tests
* Gather data for behaviour clone from good github heuristic bot
* Corner case: It is possible that you will find that you cannot use any of your cards to make a legal move. If this happens - and only then - you must pass your turn. 
  <br/>None of your pawns will move. But like the river that constantly flows, you cannot remain unchanged: you must still choose one of the two cards in front of you, place it to the left of the playmat and rotate it, then take the card from the right side of the board.

#### Lower

* Wrap flask app into a class instead of globals
* Make FE display intermediate state between user and agent move
* FE display bot vs bot
  
#### General

* Test and fix bugs
* Player is always player 1 and bot player 2 is this OK?
