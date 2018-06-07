from lab.envs.mujoco.mujoco_env import MujocoEnv
# ^^^^^ so that user gets the correct error
# message if mujoco is not installed correctly
from lab.envs.mujoco.ant import AntEnv
from lab.envs.mujoco.half_cheetah import HalfCheetahEnv
from lab.envs.mujoco.hopper import HopperEnv
from lab.envs.mujoco.walker2d import Walker2dEnv
from lab.envs.mujoco.humanoid import HumanoidEnv
from lab.envs.mujoco.inverted_pendulum import InvertedPendulumEnv
from lab.envs.mujoco.inverted_double_pendulum import InvertedDoublePendulumEnv
from lab.envs.mujoco.reacher import ReacherEnv
from lab.envs.mujoco.swimmer import SwimmerEnv
from lab.envs.mujoco.humanoidstandup import HumanoidStandupEnv
from lab.envs.mujoco.pusher import PusherEnv
from lab.envs.mujoco.thrower import ThrowerEnv
from lab.envs.mujoco.striker import StrikerEnv

from lab.envs.mujoco.swimmer_bandits import SwimmerBanditsEnv
from lab.envs.mujoco.ant_bandits import AntBanditsEnv
from lab.envs.mujoco.obstacles import Obstacles

from lab.envs.mujoco.ant_movement import AntMovementEnv
from lab.envs.mujoco.ant_obstacles import AntObstaclesEnv
from lab.envs.mujoco.ant_obstaclesbig import AntObstaclesBigEnv
from lab.envs.mujoco.ant_obstaclesgen import AntObstaclesGenEnv
from lab.envs.mujoco.humanoid_course import HumanoidCourseEnv
from lab.envs.mujoco.humanoid_seq import HumanoidSeqEnv
