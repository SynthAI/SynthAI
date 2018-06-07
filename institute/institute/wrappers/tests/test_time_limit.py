import lab
import time
import institute
from lab.envs import register
from institute import wrappers

register(
    id='test.SecondsLimitDummyVNCEnv-v0',
    entry_point='institute.envs:DummyVNCEnv',
    max_episode_seconds=0.1,
    tags={
        'vnc': True,
        }
    )

register(
    id='test.StepsLimitDummyVNCEnv-v0',
    entry_point='institute.envs:DummyVNCEnv',
    max_episode_steps=2,
    tags={
        'vnc': True,
        }
    )


def test_steps_limit_restart():
    env = lab.make('test.StepsLimitDummyVNCEnv-v0')
    env.configure(_n=1)
    env = wrappers.TimeLimit(env)
    env.reset()

    assert env._max_episode_seconds == None
    assert env._max_episode_steps == 2

    # Episode has started
    _, _, done, info = env.step([[]])
    assert done == [False]

    # Limit reached, now we get a done signal and the env resets itself
    _, _, done, info = env.step([[]])
    assert done == [True]
    assert env._elapsed_steps == 0


def test_steps_limit_restart_unused_when_not_wrapped():
    env = lab.make('test.StepsLimitDummyVNCEnv-v0')
    env.configure(_n=1)
    env.reset()

    for i in range(10):
        _, _, done, info = env.step([[]])
        assert done == [False]


def test_seconds_limit_restart():
    env = lab.make('test.SecondsLimitDummyVNCEnv-v0')
    env.configure(_n=1)
    env = wrappers.TimeLimit(env)
    env.reset()

    assert env._max_episode_seconds == 0.1
    assert env._max_episode_steps == None

    # Episode has started
    _, _, done, info = env.step([[]])
    assert done == [False]

    # Not enough time has passed
    _, _, done, info = env.step([[]])
    assert done == [False]

    time.sleep(0.2)

    # Limit reached, now we get a done signal and the env resets itself
    _, _, done, info = env.step([[]])
    assert done == [True]


def test_default_time_limit():
    # We need an env without a default limit
    register(
        id='test.NoLimitDummyVNCEnv-v0',
        entry_point='institute.envs:DummyVNCEnv',
        tags={
            'vnc': True,
            },
    )

    env = lab.make('test.NoLimitDummyVNCEnv-v0')
    env.configure(_n=1)
    env = wrappers.TimeLimit(env)
    env.reset()

    assert env._max_episode_seconds == wrappers.time_limit.DEFAULT_MAX_EPISODE_SECONDS
    assert env._max_episode_steps == None