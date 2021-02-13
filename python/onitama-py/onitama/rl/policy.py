import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers as tf_layers
from stable_baselines.common.tf_layers import conv, conv_to_fc
from stable_baselines.deepq.policies import DQNPolicy


def cnn_extractor_onitama(scaled_images, n_obs=9, n_filters_out=50, filter_size=5, **kwargs):
    """
    CNN with 5 x 5 x 50 (50 = 25 x 2) outputs, that is masked by 2nd half of inputs
    :param scaled_images: (TensorFlow Tensor) Image input placeholder (Batch size x Obs shape)
    :param n_obs: number of final dimension that is for observations, rest for mask
    :param kwargs: (dict) Extra keywords parameters for the convolutional layers of the CNN
    :return: (TensorFlow Tensor) The CNN output layer
    """
    activ = tf.nn.relu
    # split into mask and
    obs = scaled_images[:, :, :, :n_obs]
    layer_1 = activ(
        conv(obs, 'c1', n_filters=32, filter_size=filter_size, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_2 = activ(
        conv(layer_1, 'c2', n_filters=64, filter_size=filter_size, stride=1, pad='SAME', init_scale=np.sqrt(2),
             **kwargs))
    layer_3 = activ(conv(layer_2, 'c3', n_filters=n_filters_out, filter_size=filter_size, stride=1, pad='SAME',
                         init_scale=np.sqrt(2), **kwargs))
    layer_3_flat = conv_to_fc(layer_3)
    return layer_3_flat


class MaskedCNNPolicy(DQNPolicy):
    """
    Policy object that implements a DQN policy, using a feed forward neural network.
    Uses part of inputs to mask the output action probability distribution.

    :param sess: (TensorFlow session) The current TensorFlow session
    :param ob_space: (Gym Space) The observation space of the environment
    :param ac_space: (Gym Space) The action space of the environment
    :param n_env: (int) The number of environments to run
    :param n_steps: (int) The number of steps to run for each environment
    :param n_batch: (int) The number of batch to run (n_envs * n_steps)
    :param reuse: (bool) If the policy is reusable or not
    :param layers: ([int]) The size of the Neural network for the policy (if None, default to [64, 64])
    :param cnn_extractor: (function (TensorFlow Tensor, ``**kwargs``): (TensorFlow Tensor)) the CNN feature extraction
    :param feature_extraction: (str) The feature extraction type ("cnn" or "mlp")
    :param obs_phs: (TensorFlow Tensor, TensorFlow Tensor) a tuple containing an override for observation placeholder
        and the processed observation placeholder respectively
    :param layer_norm: (bool) enable layer normalisation
    :param dueling: (bool) if true double the output MLP to compute a baseline for action scores
    :param act_fun: (tf.func) the activation function to use in the neural network.
    :param kwargs: (dict) Extra keyword arguments for the nature CNN feature extraction
    """
    def __init__(self, sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse=False, layers=None,
                 cnn_extractor=cnn_extractor_onitama, feature_extraction="cnn",
                 obs_phs=None, layer_norm=False, dueling=False, act_fun=tf.nn.relu, **kwargs):
        super(MaskedCNNPolicy, self).__init__(sess, ob_space, ac_space, n_env, n_steps,
                                                n_batch, dueling=dueling, reuse=reuse,
                                                scale=(feature_extraction == "cnn"), obs_phs=obs_phs)

        self._kwargs_check(feature_extraction, kwargs)

        self.n_obs = 9

        if layers is None:
            layers = [64, 64]

        with tf.variable_scope("model", reuse=reuse):
            with tf.variable_scope("action_value"):
                extracted_features = cnn_extractor(self.processed_obs, n_obs=self.n_obs)
                action_out = extracted_features

                action_scores = tf_layers.fully_connected(action_out, num_outputs=self.n_actions)

            if self.dueling:
                with tf.variable_scope("state_value"):
                    state_out = extracted_features
                    for layer_size in layers:
                        state_out = tf_layers.fully_connected(state_out, num_outputs=layer_size, activation_fn=None)
                        if layer_norm:
                            state_out = tf_layers.layer_norm(state_out, center=True, scale=True)
                        state_out = act_fun(state_out)
                    state_score = tf_layers.fully_connected(state_out, num_outputs=1, activation_fn=None)
                action_scores_mean = tf.reduce_mean(action_scores, axis=1)
                action_scores_centered = action_scores - tf.expand_dims(action_scores_mean, axis=1)
                q_out = state_score + action_scores_centered
            else:
                q_out = action_scores

        # TODO: should be applied before q or after (ie. right before softmax)?
        mask_inp = self.processed_obs[:, :, :, self.n_obs:]
        mask_flat = conv_to_fc(mask_inp)
        # get a mask as tf.float32.min for invalid and 1s for valid
        self.mask = self.apply_mask(tf.ones_like(mask_flat), mask_flat)
        # get masked q values
        masked_q = self.apply_mask(q_out, mask_flat)
        self.q_values = masked_q
        self._setup_init()

    def apply_mask(self, values, mask_flat):
        # if it's masked, tf.float32.min, if it's valid then 1, to sample only valid
        masked = tf.where(mask_flat > 0, values, tf.fill(tf.shape(values), tf.float32.min))
        return masked

    def step(self, obs, state=None, mask=None, deterministic=True):
        """
        Returns the actions, q_values, states for a single step

        :param obs: (np.ndarray float or int) The current observation of the environment
        :param state: (np.ndarray float) The last states (used in recurrent policies)
        :param mask: (np.ndarray float) The last masks (used in recurrent policies)
        :param deterministic: (bool) Whether or not to return deterministic actions.
        :return: (np.ndarray int, np.ndarray float, np.ndarray float) actions, q_values, states
        """
        q_values, actions_proba = self.sess.run([self.q_values, self.policy_proba], {self.obs_ph: obs})
        if deterministic:
            actions = np.argmax(q_values, axis=1)
        else:
            # Unefficient sampling
            # TODO: replace the loop
            # maybe with Gumbel-max trick ? (http://amid.fish/humble-gumbel)
            actions = np.zeros((len(obs),), dtype=np.int64)
            for action_idx in range(len(obs)):
                actions[action_idx] = np.random.choice(self.n_actions, p=actions_proba[action_idx])
        return actions, q_values, None

    def proba_step(self, obs, state=None, mask=None):
        """
        Returns the action probability for a single step

        :param obs: (np.ndarray float or int) The current observation of the environment
        :param state: (np.ndarray float) The last states (used in recurrent policies)
        :param mask: (np.ndarray float) The last masks (used in recurrent policies)
        :return: (np.ndarray float) the action probability
        """
        return self.sess.run(self.policy_proba, {self.obs_ph: obs})