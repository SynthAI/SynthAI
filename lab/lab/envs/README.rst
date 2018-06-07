# Envs

These are the core integrated environments. Note that we may later
restructure any of the files, but will keep the environments available
at the relevant package's top-level. So for example, you should access
`AntEnv` as follows:

```
# Will be supported in future releases
from lab.envs import mujoco
mujoco.AntEnv
```

Rather than:

```
# May break in future releases
from lab.envs.mujoco import ant
ant.AntEnv
```

## How to create new environments for Lab

* Create a new repo called lab-foo, which should also be a PIP package.

* A good example is https://github.com/synthai/lab-soccer.

* It should have at least the following files:
  ```sh
  lab-foo/
    README.md
    setup.py
    lab_foo/
      __init__.py
      envs/
        __init__.py
        foo_env.py
        foo_extrahard_env.py
  ```

* `lab-foo/setup.py` should have:

  ```python
  from setuptools import setup

  setup(name='lab_foo',
        version='0.0.1',
        install_requires=['lab']  # And any other dependencies foo needs
  )  
  ```

* `lab-foo/lab_foo/__init__.py` should have:
  ```python
  from lab.envs.registration import register

  register(
      id='foo-v0',
      entry_point='lab_foo.envs:FooEnv',
  )
  register(
      id='foo-extrahard-v0',
      entry_point='lab_foo.envs:FooExtraHardEnv',
  )
  ```

* `lab-foo/lab_foo/envs/__init__.py` should have:
  ```python
  from lab_foo.envs.foo_env import FooEnv
  from lab_foo.envs.foo_extrahard_env import FooExtraHardEnv
  ```

* `lab-foo/lab_foo/envs/foo_env.py` should look something like:
  ```python
  import lab
  from lab import error, spaces, utils
  from lab.utils import seeding

  class FooEnv(lab.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
      ...
    def step(self, action):
      ...
    def reset(self):
      ...
    def render(self, mode='human', close=False):
      ...
  ```

## How to add new environments to Lab, within this repo (not recommended for new environments)

1. Write your environment in an existing collection or a new collection. All collections are subfolders of `/lab/envs'.
2. Import your environment into the `__init__.py` file of the collection. This file will be located at `/lab/envs/my_collection/__init__.py`. Add `from lab.envs.my_collection.my_awesome_env import MyEnv` to this file.
3. Register your env in `/lab/envs/__init__.py`:

 ```
register(
		id='MyEnv-v0',
		entry_point='lab.envs.my_collection:MyEnv',
)
```

4. Add your environment to the scoreboard in `/lab/scoreboard/__init__.py`:

 ```
add_task(
		id='MyEnv-v0',
		summary="Super cool environment",
		group='my_collection',
		contributor='mygithubhandle',
)
```
