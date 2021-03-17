from onitama.game import PvBot, State, get_move, Piece, PvP, Winner
from onitama.rl import RandomAgent, SimpleAgent
import gym
import numpy as np
import copy


def flip_pos(pos):
    newPos = np.subtract([4, 4], pos)
    return [int(newPos[0]), int(newPos[1])]


def flip_card(card):
    return list(np.flip(np.flip(card, 0), 1))


def flip_player(player):
    player_flipped = copy.deepcopy(player)
    player_flipped.cards = [flip_card(c) for c in player.cards]
    player_flipped.king = Piece(flip_pos(player.king.pos), -1)
    player_flipped.pawns = [Piece(flip_pos(p.pos), i) for i, p in enumerate(player.pawns)]
    return player_flipped


def flip_game_view(game):
    """
    Changes from p1 view (default) to p2 view, as though board has rotated or players swapped seats
    Not same as flipping
    Returns a PvP object with a flipped board (ie. from player 2's view)
    """
    game_flipped = PvP(game.seed, game.verbose, game.playerStart)
    game_flipped.winner = game.winner
    game_flipped.isPlayer1 = game.isPlayer1
    game_flipped.player1 = flip_player(game.player1)
    game_flipped.player2 = flip_player(game.player2)
    game_flipped.spare_card = flip_card(game_flipped.spare_card)
    return game_flipped


def get_board_state(player_dict):
    pawns = np.zeros((5, 5, 1))
    king = np.zeros((5, 5, 1))
    for i, j in player_dict["pawns"]:
        pawns[i][j] = 1
    k, l = player_dict["king"]
    king[k][l] = 1
    return pawns, king


def moveToMask(move, player):
    """
    :return: (a, b, c) tuple the indices of the action for mask = 1
    """
    # 5 x 5 grid is pr(pickup piece here)
    piecePos = player.king.get() if move.isKing else player.pawns[move.i].get()
    # the next is 5 x 5 spaces x 2 cards
    # card id is 0 or 1
    move_ravel = np.ravel_multi_index((piecePos[0], piecePos[1], move.pos[0], move.pos[1], move.cardId),
                                      (5, 5, 5, 5, 2))
    mask = np.unravel_index(move_ravel, (5, 5, 50))
    return mask


def _get_piece(piece_pos, player):
    if np.array_equal(piece_pos, player.king.get()):
        return True, -1
    for i, pawn in enumerate(player.pawns):
        if np.array_equal(piece_pos, pawn.get()):
            return False, i


def get_piece(piece_pos, game, isPlayer1):
    """
    :return: isKing, i
    """
    if isPlayer1:
        return _get_piece(piece_pos, game.player1)
    else:
        return _get_piece(piece_pos, game.player2)


def get_mask(game, isPlayer1, mask_shape=(5, 5, 50)):
    """
    (5 x 5 x 50) (same shape as agent output)
    Returns the mask over valid moves
    Binary tensor.
    """
    game = get_game_maybe_flipped(game, isPlayer1)
    mask = np.zeros(mask_shape)
    player = game.player1 if isPlayer1 else game.player2
    assert len(game.get_valid_moves(player, isPlayer1)) > 0, "No valid moves for masking"
    for move in game.get_valid_moves(player, isPlayer1):
        ac = moveToMask(move, player)
        mask[ac] = 1
        # print("Valid move in mask: {}".format(np.ravel_multi_index(ac, mask_shape)))
    return mask


def _get_obs(game, isPlayer1):
    """
    Returns (5, 5, 9) see above for observation format
    """
    game = get_game_maybe_flipped(game, isPlayer1)
    # see game class for API
    game_state = State(game.get())
    obs = []
    # cards
    obs.append(np.stack(game_state.player1_dict["cards"], -1))
    obs.append(np.stack(game_state.player2_dict["cards"], -1))
    obs.append(np.expand_dims(game_state.spare_card, -1))
    # board
    pawns_p1, king_p1 = get_board_state(game_state.player1_dict)
    obs.append(pawns_p1)
    obs.append(king_p1)
    pawns_p2, king_p2 = get_board_state(game_state.player2_dict)
    obs.append(pawns_p2)
    obs.append(king_p2)
    return np.concatenate(obs, -1)


def actionToMove(ac_chosen, game, isPlayer1, mask_shape):
    """
    :param ac_chosen: reshaped action (piece pos i, piece pos j, board x card data)
    :return: Move() object
    """
    game = get_game_maybe_flipped(game, isPlayer1)
    ac_ravel = np.ravel_multi_index(ac_chosen, mask_shape)
    (piece_pos_i, piece_pos_j, pos_i, pos_j, card_id) = np.unravel_index(ac_ravel, (5, 5, 5, 5, 2))
    # wrap in int() to avoid non-serialisable errors
    piece_pos = [int(piece_pos_i), int(piece_pos_j)]
    pos = [int(pos_i), int(pos_j)]
    if not isPlayer1:
        pos = flip_pos(pos)
    piece = get_piece(piece_pos, game, isPlayer1)
    isKing, i = piece
    move = get_move(pos, isKing, card_id, i)
    return move


def get_game_maybe_flipped(game, isPlayer1):
    return game if isPlayer1 else flip_game_view(game)


class OnitamaEnv(gym.Env):
    """
    Defaults to player 1
    See README for obs and ac space definitions
    """

    def __init__(self, seed, agent_type=SimpleAgent, isPlayer1=True, verbose=True):
        super(OnitamaEnv, self).__init__()
        self.game = PvBot(agent_type(seed), seed, verbose=verbose)
        self.observation_space = gym.spaces.Box(np.zeros((5, 5, 59)), np.ones((5, 5, 59)))
        self.action_space = gym.spaces.Discrete(5 * 5 * 25 * 2)
        self.mask_shape = (5, 5, 50)
        self.isPlayer1 = isPlayer1
        self._seed = seed

    def step(self, ac):
        ac = np.squeeze(ac)
        # action is index into 5 x 5 x 50
        ac = np.unravel_index(ac, self.mask_shape)
        move = actionToMove(ac, self.game, self.isPlayer1, self.mask_shape)
        self.game.step(move)
        self.game.stepBot()

        info = {}
        done = False
        # win, lose or draw
        if self.game.winner is not Winner.noWin:
            done = True
            info["winner"] = self.game.winner.value
            # success if controlled winning player
            info["is_success"] = self.game.winner.value == (1 + int(not self.isPlayer1))
        return self.get_obs(), self.get_reward(), done, info

    def reset(self):
        self.game.reset()
        # print()
        # print(*[" ".join(map(str, a)) + "\n" for a in self.game.player1.cards[0]])
        # print(*[" ".join(map(str, a)) + "\n" for a in self.game.spare_card])
        return self.get_obs()

    def render(self, mode='human'):
        pass

    def get_obs(self):
        """
        Observation and mask for valid actions
        :return:
        """
        return np.concatenate([_get_obs(self.game, self.isPlayer1), get_mask(self.game, self.isPlayer1)], -1)

    def get_reward(self):
        # can get game state by eg.
        # self.game.player1
        move_forwards = 0
        reward_win = 0

        player = self.game.player1 if self.game.isPlayer1 else self.game.player2
        opponent = self.game.player2 if self.game.isPlayer1 else self.game.player1

        
        state = State(self.game.get())

        win_dict = {player.player:1,opponent.player:-1,"noWin":0,"draw":0}
        reward_win = win_dict[self.game.winner.name]

        player = self.game.player1 if self.game.isPlayer1 else self.game.player2

        # Get number of rows moved
        if player.last_move is not None:
            rows_moved = player.last_move.pos[0] - player.last_pos[0]
            row_orientation = 1 if not self.isPlayer1 else -1
            move_forwards = max(0, rows_moved * row_orientation)

        pawns_taken = 1 if opponent.lost_pawn_last_move else -1 if player.lost_pawn_last_move else 0

        # Discuss weights assigned to each reward with team
        reward_weights = {
            "move_forwards": 0.01,
            "take_pawn": 0.1,
            "win": 1.0,
        }
        reward_dict = {
            "move_forwards": move_forwards,
            "take_pawn": pawns_taken,
            "win": reward_win
        }
        reward = 0
        for k, r in reward_dict.items():
            reward += r * reward_weights[k]
        return reward

    def seed(self, seed):
        self._seed = seed
        np.random.seed(seed)


class OnitamaSelfPlayEnv(gym.Env):
    """
    An env where step and reward is called for each player 1 and 2 being RL
    Assume p1 to be the main player for training
    """

    def __init__(self, seed, verbose=True, deterministicSelfPlay=False, nStepsSelfPlay=int(1e3)):
        super(OnitamaSelfPlayEnv, self).__init__()
        self.game = PvP(seed, verbose=verbose)
        self.observation_space = gym.spaces.Box(np.zeros((5, 5, 59)), np.ones((5, 5, 59)))
        self.action_space = gym.spaces.Discrete(5 * 5 * 25 * 2)
        self.mask_shape = (5, 5, 50)
        self._seed = seed
        # the model weights for self play
        self.selfPlayModel = None
        self.deterministicSelfPlay = deterministicSelfPlay

    def step(self, ac):
        # run the training model action
        move = self.getMove(ac)
        self.game.step(move)
        # step the self play action
        acSelfPlay, _ = self.selfPlayModel.predict([self.get_obs()], deterministic=self.deterministicSelfPlay)
        moveSelfPlay = self.getMove(acSelfPlay)
        self.game.step(moveSelfPlay)

        info = {}
        done = False
        # win, lose or draw
        if self.game.winner is not Winner.noWin:
            done = True
            info["winner"] = self.game.winner.value
            # success if player 1 won
            info["is_success"] = self.game.winner.value == 1
        return self.get_obs(), self.get_reward(), done, info

    def getMove(self, ac):
        ac = np.squeeze(ac)
        # action is index into 5 x 5 x 50
        ac = np.unravel_index(ac, self.mask_shape)
        move = actionToMove(ac, self.game, self.game.isPlayer1, self.mask_shape)
        return move

    def reset(self):
        assert self.selfPlayModel, "No model set"
        self.game.reset()
        return self.get_obs()

    def render(self, mode='human'):
        pass

    def get_obs(self):
        """
        Observation and mask for valid actions
        :return:
        """
        return np.concatenate([_get_obs(self.game, self.game.isPlayer1), get_mask(self.game, self.game.isPlayer1)], -1)

    def get_reward(self):
        # can get game state by eg.
        # self.game.player1
        move_forwards = 0
        reward_win = 0

        player = self.game.player1 if self.game.isPlayer1 else self.game.player2
        opponent = self.game.player2 if self.game.isPlayer1 else self.game.player1

        
        state = State(self.game.get())

        win_dict = {player.player:1,opponent.player:-1,"noWin":0,"draw":0}
        reward_win = win_dict[self.game.winner.name]

        player = self.game.player1 if self.game.isPlayer1 else self.game.player2
        

        # Get number of rows moved
        if player.last_move is not None:
            rows_moved = player.last_move.pos[0] - player.last_pos[0]
            row_orientation = 1 if not self.game.isPlayer1 else -1
            move_forwards = max(0, rows_moved * row_orientation)

        pawns_taken = 1 if opponent.lost_pawn_last_move else -1 if player.lost_pawn_last_move else 0

        # Discuss weights assigned to each reward with team
        reward_weights = {
            "move_forwards": 0.005,
            "take_pawn": 0.05,
            "win": 1.0,
        }
        reward_dict = {
            "move_forwards": move_forwards,
            "take_pawn": pawns_taken,
            "win": reward_win
        }
        reward = 0
        for k, r in reward_dict.items():
            reward += r * reward_weights[k]
        return reward

    def seed(self, seed):
        self._seed = seed
        np.random.seed(seed)

    def setSelfPlayModel(self, model):
        self.selfPlayModel = model
