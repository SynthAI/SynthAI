from lab.envs.registration import register
#from lab.scoreboard.registration import add_task, add_group

register(
    id='Synthtraining InvertedPendulum-v1',
    entry_point='synthtraining :Synthtraining InvertedPendulum',
    max_episode_steps=1000,
    reward_threshold=950.0,
    tags={ "pg_complexity": 1*1000000 },
    )
register(
    id='Synthtraining InvertedPendulumSwingup-v1',
    entry_point='synthtraining :Synthtraining InvertedPendulumSwingup',
    max_episode_steps=1000,
    reward_threshold=800.0,
    tags={ "pg_complexity": 1*1000000 },
    )
register(
    id='Synthtraining InvertedDoublePendulum-v1',
    entry_point='synthtraining :Synthtraining InvertedDoublePendulum',
    max_episode_steps=1000,
    reward_threshold=9100.0,
    tags={ "pg_complexity": 1*1000000 },
    )

register(
    id='Synthtraining Reacher-v1',
    entry_point='synthtraining :Synthtraining Reacher',
    max_episode_steps=150,
    reward_threshold=18.0,
    tags={ "pg_complexity": 1*1000000 },
    )

register(
    id='Synthtraining Hopper-v1',
    entry_point='synthtraining :Synthtraining Hopper',
    max_episode_steps=1000,
    reward_threshold=2500.0,
    tags={ "pg_complexity": 8*1000000 },
    )
register(
    id='Synthtraining Walker2d-v1',
    entry_point='synthtraining :Synthtraining Walker2d',
    max_episode_steps=1000,
    reward_threshold=2500.0,
    tags={ "pg_complexity": 8*1000000 },
    )
register(
    id='Synthtraining HalfCheetah-v1',
    entry_point='synthtraining :Synthtraining HalfCheetah',
    max_episode_steps=1000,
    reward_threshold=3000.0,
    tags={ "pg_complexity": 8*1000000 },
    )

register(
    id='Synthtraining Ant-v1',
    entry_point='synthtraining :Synthtraining Ant',
    max_episode_steps=1000,
    reward_threshold=2500.0,
    tags={ "pg_complexity": 8*1000000 },
    )

register(
    id='Synthtraining Humanoid-v1',
    entry_point='synthtraining :Synthtraining Humanoid',
    max_episode_steps=1000,
    reward_threshold=3500.0,
    tags={ "pg_complexity": 100*1000000 },
    )
register(
    id='Synthtraining HumanoidFlagrun-v1',
    entry_point='synthtraining :Synthtraining HumanoidFlagrun',
    max_episode_steps=1000,
    reward_threshold=2000.0,
    tags={ "pg_complexity": 200*1000000 },
    )
register(
    id='Synthtraining HumanoidFlagrunHarder-v1',
    entry_point='synthtraining :Synthtraining HumanoidFlagrunHarder',
    max_episode_steps=1000,
    tags={ "pg_complexity": 300*1000000 },
    )


# Atlas

register(
    id='Synthtraining AtlasForwardWalk-v1',
    entry_point='synthtraining :Synthtraining AtlasForwardWalk',
    max_episode_steps=1000,
    tags={ "pg_complexity": 200*1000000 },
    )


# Multiplayer

register(
    id='Synthtraining Pong-v1',
    entry_point='synthtraining :Synthtraining Pong',
    max_episode_steps=1000,
    tags={ "pg_complexity": 20*1000000 },
    )

from synthtraining .lab_pendulums import Synthtraining InvertedPendulum
from synthtraining .lab_pendulums import Synthtraining InvertedPendulumSwingup
from synthtraining .lab_pendulums import Synthtraining InvertedDoublePendulum
from synthtraining .lab_reacher import Synthtraining Reacher
from synthtraining .lab_mujoco_walkers import Synthtraining Hopper
from synthtraining .lab_mujoco_walkers import Synthtraining Walker2d
from synthtraining .lab_mujoco_walkers import Synthtraining HalfCheetah
from synthtraining .lab_mujoco_walkers import Synthtraining Ant
from synthtraining .lab_mujoco_walkers import Synthtraining Humanoid
from synthtraining .lab_humanoid_flagrun import Synthtraining HumanoidFlagrun
from synthtraining .lab_humanoid_flagrun import Synthtraining HumanoidFlagrunHarder
from synthtraining .lab_atlas import Synthtraining AtlasForwardWalk
from synthtraining .lab_pong import Synthtraining Pong
