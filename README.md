
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

#### Notes

* Cards not shuffled (in get_init_cards, do_shuffle=False)

#### Higher priority

* ? - Try hparams, esp. buffer and batch size, LR, try param noise?
* O - update notes that mask now input as an input too
* O - am thinking it needs to learn based on the latest opponent  
        try DQN with smaller buffer size? 
        try PPO?
* ? - what to print out to monitor self play?  
* G - Fix the no moves corner case and test - note I removed test case from the get_init_cards and set it up
    in test_env.py. If it's a major difficulty then can revert that back but bit cleaner to keep tests together
* T - check if any of reward need be flipped
* T - enum for win
* ? - try (vs. simple agent) training with held out cards and how it evals with them
* ? - Implement for env not using player start bsaed on cards 
    (set in game playerStart=None instead of playerStart=1 rather to use starting player based on cards)
* ? - look into self play 
        Seems alpha zero just runs the current weights against themselves - do both train or just p1?
        alphaGo zero stores best model and overwrites it if current weights better
  
* O - env needs to account for starting cards (then set to None rather than 1 in game)
* T - Get running on MLP server
* ? - check seeding is repeatable on train - seems ok on eval
* ? - Check ac and obs spaces and bounds
* ? - get github agent into our system (same as random/simple agent) - mostly as eval but worth trying to train with to
* ? - make a cmd line print out of board state would be useful debugging

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

Tried DQN self play with a 5000 buffer size and it didnt seem to train well but only ran 32,000 timesteps

Checked eval env as another self play instance and the games seemed fairly well matched 2-3/5 wins so that 
seems to be working ok

Tried 
                 learning_rate=1e-4,
                 buffer_size=100000,
                 batch_size=256,
        with reward for move forward as 0.001
Training was much slower and no better

With shuffled cards and prioritised replay

300k epochs

Mean reward: -0.5558500000000001
Std reward: 0.8145609415507227
Min reward: -1.145
Max reward: 1.055
Mean episode length: 26.53
Std episode length: 22.09997963799967
Min episode length: 3
Max episode length: 142
Won 23 / 100





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