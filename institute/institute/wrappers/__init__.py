import lab
import institute.wrappers.experimental
from institute import envs, spaces
from institute.wrappers import lab_core_sync
from institute.wrappers.blocking_reset import BlockingReset
from institute.wrappers.diagnostics import Diagnostics
from institute.wrappers.lab_core import LabCoreAction, LabCoreObservation, CropAtari
from institute.wrappers.joint import Joint
from institute.wrappers.logger import Logger
from institute.wrappers.monitoring import Monitor
from institute.wrappers.multiprocessing_env import WrappedMultiprocessingEnv, EpisodeID
from institute.wrappers.recording import Recording
from institute.wrappers.render import Render
from institute.wrappers.throttle import Throttle
from institute.wrappers.time_limit import TimeLimit
from institute.wrappers.timer import Timer
from institute.wrappers.vectorize import Vectorize, Unvectorize, WeakUnvectorize
from institute.wrappers.vision import Vision


def wrap(env):
    return Timer(Render(Throttle(env)))

def WrappedVNCEnv():
    return wrap(envs.VNCEnv())

def WrappedLabCoreEnv(lab_core_id, fps=None, rewarder_observation=False):
    # Don't need to store the ID on the instance; it'll be retrieved
    # directly from the spec
    env = wrap(envs.VNCEnv(fps=fps))
    if rewarder_observation:
        env = LabCoreObservation(env, lab_core_id=lab_core_id)
    return env

def WrappedLabCoreSyncEnv(lab_core_id, fps=60, rewarder_observation=False):
    spec = lab.spec(lab_core_id)
    env = lab_core_sync.LabCoreSync(BlockingReset(wrap(envs.VNCEnv(fps=fps))))
    if rewarder_observation:
        env = LabCoreObservation(env, lab_core_id=lab_core_id)
    elif spec._entry_point.startswith('lab.envs.atari:'):
        env = CropAtari(env)

    return env

def WrappedFlashgamesEnv():
    keysym = spaces.KeyEvent.by_name('`').key
    return wrap(envs.VNCEnv(probe_key=keysym))

def WrappedInternetEnv(*args, **kwargs):
    return wrap(envs.InternetEnv(*args, **kwargs))

def WrappedStarCraftEnv(*args, **kwargs):
    return wrap(envs.StarCraftEnv(*args, **kwargs))

def WrappedGTAVEnv(*args, **kwargs):
    return wrap(envs.GTAVEnv(*args, **kwargs))

def WrappedWorldOfGooEnv(*args, **kwargs):
    return wrap(envs.WorldOfGooEnv(*args, **kwargs))
