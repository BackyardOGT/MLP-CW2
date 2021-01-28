import numpy as np
from stable_baselines.common.policies import ActorCriticPolicy
from stable_baselines.common.tf_layers import conv, linear, conv_to_fc
import tensorflow as tf


class RandomAgent:
    def __init__(self):
        np.random.seed(1123)

    def get_action(self, state):
        ac = np.random.choice(state.get_valid_moves(state.player2))
        return ac


def apply_mask(activations, mask):
    print(np.shape(activations))
    return activations * mask


def cnn_extractor_onitama(scaled_images, n_obs=10, n_filters_out=50, filter_size=5, **kwargs):
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
    mask = scaled_images[:, :, :, n_obs:]
    print(np.shape(obs))
    print(np.shape(mask))
    layer_1 = activ(
        conv(obs, 'c1', n_filters=32, filter_size=filter_size, stride=1, pad='SAME', init_scale=np.sqrt(2), **kwargs))
    layer_2 = activ(
        conv(layer_1, 'c2', n_filters=64, filter_size=filter_size, stride=1, pad='SAME', init_scale=np.sqrt(2),
             **kwargs))
    layer_3 = activ(conv(layer_2, 'c3', n_filters=n_filters_out, filter_size=filter_size, stride=1, pad='SAME',
                         init_scale=np.sqrt(2), **kwargs))
    layer_3_flat = conv_to_fc(layer_3)
    mask_flat = conv_to_fc(mask)
    layer_3_flat_masked = apply_mask(layer_3_flat, mask_flat)
    return layer_3_flat_masked


class MaskedCNNPolicy(ActorCriticPolicy):
    """
    Policy object that implements actor critic, using a CNN.
    Uses part of inputs to mask the output action probability distribution.

    :param sess: (TensorFlow session) The current TensorFlow session
    :param ob_space: (Gym Space) The observation space of the environment
    :param ac_space: (Gym Space) The action space of the environment
    :param n_env: (int) The number of environments to run
    :param n_steps: (int) The number of steps to run for each environment
    :param n_batch: (int) The number of batch to run (n_envs * n_steps)
    :param reuse: (bool) If the policy is reusable or not
    :param layers: ([int]) (deprecated, use net_arch instead) The size of the Neural network for the policy
        (if None, default to [64, 64])
    :param net_arch: (list) Specification of the actor-critic policy network architecture (see mlp_extractor
        documentation for details).
    :param act_fun: (tf.func) the activation function to use in the neural network.
    :param cnn_extractor: (function (TensorFlow Tensor, ``**kwargs``): (TensorFlow Tensor)) the CNN feature extraction
    :param feature_extraction: (str) The feature extraction type ("cnn" or "mlp")
    :param kwargs: (dict) Extra keyword arguments for the CNN feature extraction
    """

    def __init__(self, sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse=False, layers=None, net_arch=None,
                 act_fun=tf.tanh, cnn_extractor=cnn_extractor_onitama, feature_extraction="cnn", **kwargs):
        super(MaskedCNNPolicy, self).__init__(sess, ob_space, ac_space, n_env, n_steps, n_batch, reuse=reuse,
                                              scale=(feature_extraction == "cnn"))

        self._kwargs_check(feature_extraction, kwargs)

        if layers is not None:
            warnings.warn("Usage of the `layers` parameter is deprecated! Use net_arch instead "
                          "(it has a different semantics though).", DeprecationWarning)
            if net_arch is not None:
                warnings.warn("The new `net_arch` parameter overrides the deprecated `layers` parameter!",
                              DeprecationWarning)

        if net_arch is None:
            if layers is None:
                layers = [64, 64]
            net_arch = [dict(vf=layers, pi=layers)]

        with tf.variable_scope("model", reuse=reuse):
            pi_latent = vf_latent = cnn_extractor(self.processed_obs, **kwargs)

            self._value_fn = linear(vf_latent, 'vf', 1)

            self._proba_distribution, self._policy, self.q_value = \
                self.pdtype.proba_distribution_from_latent(pi_latent, vf_latent, init_scale=0.01)

        self._setup_init()

    def step(self, obs, state=None, mask=None, deterministic=False):
        if deterministic:
            action, value, neglogp = self.sess.run([self.deterministic_action, self.value_flat, self.neglogp],
                                                   {self.obs_ph: obs})
        else:
            action, value, neglogp = self.sess.run([self.action, self.value_flat, self.neglogp],
                                                   {self.obs_ph: obs})
        return action, value, self.initial_state, neglogp

    def proba_step(self, obs, state=None, mask=None):
        return self.sess.run(self.policy_proba, {self.obs_ph: obs})

    def value(self, obs, state=None, mask=None):
        return self.sess.run(self.value_flat, {self.obs_ph: obs})
