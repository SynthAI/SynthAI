import distutils.version
import os
import sys
import warnings

from lab import error
from lab.utils import reraise
from lab.version import VERSION as __version__

from lab.core import Env, GoalEnv, Space, Wrapper, ObservationWrapper, ActionWrapper, RewardWrapper
from lab.envs import make, spec
from lab import logger

def undo_logger_setup():
    warnings.warn("lab.undo_logger_setup is deprecated. lab no longer modifies the global logging configuration")

# Upon one acccess to lab.spaces.foo (or a manually-called import
# lab.spaces), lab.spaces will be imported and override the stub
# object.
class Spaces(object):
    def __getattr__(self, k):
        warnings.warn('DEPRECATION WARNING: to improve load times, lab no longer automatically loads lab.spaces. Please run "import lab.spaces" to load lab.spaces on your own. This warning will turn into an error in a future version of lab.')
        import lab.spaces
        return getattr(lab.spaces, k)
spaces = Spaces()

class Wrappers(object):
    def __getattr__(self, k):
        warnings.warn('DEPRECATION WARNING: to improve load times, lab no longer automatically loads lab.wrappers. Please run "import lab.wrappers" to load lab.wrappers on your own. This warning will turn into an error in a future version of lab.')
        import lab.wrappers
        return getattr(lab.wrappers, k)
wrappers = Wrappers()

__all__ = ["Env", "Space", "Wrapper", "make", "spec", "wrappers", "spaces"]
