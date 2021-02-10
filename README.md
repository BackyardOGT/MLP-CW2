
## Usage

```
git clone ....
cd MLP-CW2
```

#### Python

See above, then

Install the python library

```
cd python/onitama-py
pip install -e .
```

And install stable baselines locally

```
cd python/stable-baselines-master
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

## Notes

Heuristic agent seems good to me when I played it with UI. 

Init RL (ie. no training) against heuristic agent looks good:

Mean reward: 0.51
Std reward: 0.10440306508910549
Min reward: 0.4
Max reward: 0.7
Mean episode length: 5.5
Std episode length: 1.6278820596099706
Min episode length: 4
Max episode length: 9
Won 0 / 10

Ran training code for a bit and it ran without error

## TODOs

* Running with fixed cards, change `do_shuffle` arg in `init_cards` to do random.

#### Higher priority

* O - taking invalid actions in evaluation callback, maybe bc tf.where?
* O - check seeding is repeatable  
* ? - Get running on MLP server
* T - Implement which pick which player starts based on cards- see onitama rules
* G - Corner case: It is possible that you will find that you cannot use any of your cards to make a legal move. If this happens - and only then - you must pass your turn. 
  <br/>None of your pawns will move. But like the river that constantly flows, you cannot remain unchanged: you must still choose one of the two cards in front of you, place it to the left of the playmat and rotate it, then take the card from the right side of the board.
  * Remove assertion in env and handle no valid moves
  * Try and make a test case


* O - Think masking for exploration works, worth checking / testing more
* O - Add square highlighting before move to show bot vs bot

* Work on reward and heuristic agent

#### Lower

* Say what bots are playing
* Check masking not making gradients explode / vanish? 
* 5 x 5 filter with 5 x 5 input and output 
* Gather data for behaviour clone from good github heuristic bot
* Wrap flask app into a class instead of globals
  
#### General

* Test and fix bugs
* Player is always player 1 and bot player 2 is this OK?
