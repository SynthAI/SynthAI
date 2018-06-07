from lab.envs.registration import register


register(
    id="wikinav-v0",
    entry_point="lab_wikinav.envs:EmbeddingWikiNavEnv",
    timestep_limit=50)
