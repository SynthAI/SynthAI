from lab.envs.registration import register


# ------------------------------------------------------------------------------
# SynthSumo environments
# ------------------------------------------------------------------------------

register(
    id='SynthSumo-Ant-vs-Ant-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['ant', 'ant'],
        'agent_densities': [13., 13.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Ant-vs-Bug-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['ant', 'bug'],
        'agent_densities': [13., 10.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Ant-vs-Spider-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['ant', 'spider'],
        'agent_densities': [13., 39.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Bug-vs-Ant-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['bug', 'ant'],
        'agent_densities': [10., 13.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Bug-vs-Bug-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['bug', 'bug'],
        'agent_densities': [10., 10.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Bug-vs-Spider-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['bug', 'spider'],
        'agent_densities': [10., 39.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Spider-vs-Ant-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['spider', 'ant'],
        'agent_densities': [39., 13.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Spider-vs-Bug-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['spider', 'bug'],
        'agent_densities': [39., 10.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)

register(
    id='SynthSumo-Spider-vs-Spider-v0',
    entry_point='synthsumo.envs:SumoEnv',
    kwargs={
        'agent_names': ['spider', 'spider'],
        'agent_densities': [39., 39.],
        'tatami_size': 2.0,
        'timestep_limit': 500,
    },
)
