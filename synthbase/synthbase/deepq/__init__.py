from synthbase.deepq import models  # noqa
from synthbase.deepq.build_graph import build_act, build_train  # noqa
from synthbase.deepq.simple import learn, load  # noqa
from synthbase.deepq.replay_buffer import ReplayBuffer, PrioritizedReplayBuffer  # noqa

def wrap_atari_dqn(env):
    from synthbase.common.atari_wrappers import wrap_deepmind
    return wrap_deepmind(env, frame_stack=True, scale=True)