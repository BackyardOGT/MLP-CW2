
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

* Implement pick which player starts
* Try person against the heuristic agent and random bot
* FE display bot vs bot and cmd line evaluation # wins, reward etc
* Corner case: It is possible that you will find that you cannot use any of your cards to make a legal move. If this happens - and only then - you must pass your turn. 
  <br/>None of your pawns will move. But like the river that constantly flows, you cannot remain unchanged: you must still choose one of the two cards in front of you, place it to the left of the playmat and rotate it, then take the card from the right side of the board.
  * Remove assertion in env and handle no valid moves
  * Try and make a test case
* Masking for actions - need to mask exploration and remove the if statement in step()
  Currently we allow invalid but return the current state and don't step the game. But this won't learn legal moves
  as the masking will zero the gradient back to the network. Would have to remove masking completely to learn valid moves.
  So will have to overwrite more of their stuff to mask exploration.
  * OR can we use parameter noise for now    
* Work on reward and heuristic agent?

#### Lower

* 5 x 5 filter with 5 x 5 input and output 
* Gather data for behaviour clone from good github heuristic bot
* Wrap flask app into a class instead of globals
* Make FE display intermediate state between user and agent move
  
#### General

* Test and fix bugs
* Player is always player 1 and bot player 2 is this OK?
