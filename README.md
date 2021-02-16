
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


## TODOs

#### Higher priority

* O - sort env to work with RL as player 2 - mirror the acs, obs and mask
* O - Add prioritised replay buffer
* O - Run on full game vs simple agent - change `do_shuffle` arg in `init_cards` to do random.
* ? - get github agent into our system (same as random/simple agent)
* ? - Check ac and obs spaces and bounds
* ? - check seeding is repeatable on train - seems ok on eval
* T - Get running on MLP server
* T ? Implement pick which player starts based on cards- see onitama rules??
* G - Fix the no moves corner case and test
* G - make simple agent work as player 2

* Work on reward and heuristic agent

#### Lower

* Label bots are playing in UI
* O - Add square highlighting before move to show bot vs bot
* Check masking not making gradients explode / vanish? 
* 5 x 5 filter with 5 x 5 input and output 
* Gather data for behaviour clone from good github heuristic bot
* Wrap flask app into a class instead of globals
  
#### General

* Test and fix bugs
* Player is always player 1 and bot player 2 is this OK?


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

#### First run

Went pretty well actually, within 5 mins you get a model close to SimpleAgent level:

Mean reward: 0.1548
Std reward: 1.0011478212531855
Min reward: -1.31
Max reward: 1.22
Mean episode length: 6.11
Std episode length: 4.749515764791186
Min episode length: 2
Max episode length: 26
Won 56 / 100

Need to work on it but v promising start!

Changed the reward to favour wins more.


#### Next run

In less than 1 hour got to beating simple agent: 

Mean reward: 0.5562999999999999
Std reward: 0.8434487595580422
Min reward: -1.155
Max reward: 1.085
Mean episode length: 5.41
Std episode length: 3.954984197187139
Min episode length: 2
Max episode length: 23
Won 78 / 100