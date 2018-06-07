import logging
import lab
import time
import numpy as np
from institute import error
from lab import spaces as lab_spaces
from institute import spaces
from institute import rewarder, vectorized
from institute.envs.vnc_core_env import translator

logger = logging.getLogger(__name__)

ATARI_HEIGHT = 210
ATARI_WIDTH = 160

def atari_vnc(up=False, down=False, left=False, right=False, z=False):
    return [spaces.KeyEvent.by_name('up', down=up),
            spaces.KeyEvent.by_name('left', down=left),
            spaces.KeyEvent.by_name('right', down=right),
            spaces.KeyEvent.by_name('down', down=down),
            spaces.KeyEvent.by_name('z', down=z)]

def lab_core_action_space(lab_core_id):
    spec = lab.spec(lab_core_id)

    if spec.id == 'CartPole-v0':
        return spaces.Hardcoded([[spaces.KeyEvent.by_name('left', down=True)],
                                 [spaces.KeyEvent.by_name('left', down=False)]])
    elif spec._entry_point.startswith('lab.envs.atari:'):
        actions = []
        env = spec.make()
        for action in env.unwrapped.get_action_meanings():
            z = 'FIRE' in action
            left = 'LEFT' in action
            right = 'RIGHT' in action
            up = 'UP' in action
            down = 'DOWN' in action
            translated = atari_vnc(up=up, down=down, left=left, right=right, z=z)
            actions.append(translated)
        return spaces.Hardcoded(actions)
    else:
        raise error.Error('Unsupported env type: {}'.format(spec.id))


class CropAtari(vectorized.ObservationWrapper):
    """
Crop the relevant portion of the monitor where an Atari enviroment resides.
"""

    def __init__(self, env):
        super(CropAtari, self).__init__(env)
        self.observation_space = lab_spaces.Box(0, 255, shape=(ATARI_HEIGHT, ATARI_WIDTH, 3))

    def _observation(self, observation_n):
        return [{'vision': ob['vision'][:ATARI_HEIGHT, :ATARI_WIDTH, :]} for ob in observation_n]

def one_hot(indices, depth):
    return np.eye(depth)[indices]

class LabCoreAction(vectorized.ActionWrapper):
    def __init__(self, env, lab_core_id=None):
        super(LabCoreAction, self).__init__(env)

        if lab_core_id is None:
            # self.spec is None while inside of the make, so we need
            # to pass lab_core_id in explicitly there. This case will
            # be hit when instantiating by hand.
            lab_core_id = self.spec._kwargs['lab_core_id']

        spec = lab.spec(lab_core_id)
        raw_action_space = lab_core_action_space(lab_core_id)

        self._actions = raw_action_space.actions
        self.action_space = lab_spaces.Discrete(len(self._actions))

        if spec._entry_point.startswith('lab.envs.atari:'):
            self.key_state = translator.AtariKeyState(lab.make(lab_core_id))
        else:
            self.key_state = None

    def _action(self, action_n):
        # Each action might be a length-1 np.array. Cast to int to
        # avoid warnings.
        return [self._actions[int(action)] for action in action_n]

    def _reverse_action(self, action_n):
        # Only works for core envs currently
        self.key_state.apply_vnc_actions(action_n)
        return one_hot(self.key_state.to_index(), self.action_space.n)

class LabCoreObservation(vectorized.Wrapper):
    def __init__(self, env, lab_core_id=None):
        super(LabCoreObservation, self).__init__(env)

        if lab_core_id is None:
            # self.spec is None while inside of the make, so we need
            # to pass lab_core_id in explicitly there. This case will
            # be hit when instantiating by hand.
            lab_core_id = self.spec._kwargs['lab_core_id']

        self._reward_n = None
        self._done_n = None
        self._info_n = None

        self._lab_core_env = lab.spec(lab_core_id).make()

    def _reset(self):
        observation_n = self.env.reset()
        self.reward_n = [0] * self.n
        self.done_n = [False] * self.n
        self.info = {'n': [{} for _ in range(self.n)]}
        new_observation_n, new_reward_n, new_done_n, new_info = self.env.step([[] for i in range(self.n)])
        rewarder.merge_n(
            observation_n, self.reward_n, self.done_n, self.info,
            new_observation_n, new_reward_n, new_done_n, new_info
        )
        return self._observation(self.done_n, self.info)

    def _step(self, action_n):
        observation_n, reward_n, done_n, info = self.env.step(action_n)
        if self.reward_n is not None:
            rewarder.merge_n(
                observation_n, reward_n, done_n, info,
                [None] * self.n, self.reward_n, self.done_n, self.info,
            )
            self.reward_n = self.done_n = self.info = None
        return self._observation(done_n, info), reward_n, done_n, info

    def _observation(self, done_n, info):
        missing = set()

        observation_n = [None] * self.n
        for i, (done, info_i) in enumerate(zip(done_n, info['n'])):
            rewarder_observation = info_i.pop('rewarder.observation', None)
            if rewarder_observation is not None:
                observation, episode_id = rewarder_observation
                observation_n[i] = self._lab_core_env.observation_space.from_jsonable(observation)

                if done:
                    # Check whether we should mask
                    completed = info_i['env_status.completed_episode_id']
                    # Observation from old!
                    if episode_id == completed:
                        logger.debug('[%d] Masking rewarder_observation on episode boundary', i)
                        observation_n[i] = None
            else:
                missing.add(i)

        if len(missing) > 0:
            logger.debug('Missing rewarder observations: %s', missing)
        return observation_n
