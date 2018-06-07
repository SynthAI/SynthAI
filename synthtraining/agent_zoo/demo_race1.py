import os, sys, subprocess
import numpy as np
import lab
import synthtraining 

if len(sys.argv)==1:
    import synthtraining .multiplayer
    stadium = synthtraining .scene_stadium.MultiplayerStadiumScene(gravity=9.8, timestep=0.0165/4, frame_skip=4)
    gameserver = synthtraining .multiplayer.SharedMemoryServer(stadium, "race", want_test_window=True)
    # We start subprocesses between constructor and serve_forever(), because constructor creates necessary pipes to connect to
    for n in range(stadium.players_count):
        subprocess.Popen([sys.executable, sys.argv[0], "race", "%i"%n])
    gameserver.serve_forever()

else:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    import tensorflow as tf
    config = tf.ConfigProto(
        inter_op_parallelism_threads=1,
        intra_op_parallelism_threads=1,
        device_count = { "GPU": 0 } )
    sess = tf.InteractiveSession(config=config)
    # If this gives you an error, try CUDA_VISIBLE_DEVICES=  (nothing visible)

    from Synthtraining Walker2d_v1_2017jul        import ZooPolicyTensorflow as PolWalker
    from Synthtraining Hopper_v1_2017jul          import ZooPolicyTensorflow as PolHopper
    from Synthtraining HalfCheetah_v1_2017jul     import ZooPolicyTensorflow as PolHalfCheetah
    from Synthtraining Humanoid_v1_2017jul        import ZooPolicyTensorflow as PolHumanoid1
    from Synthtraining HumanoidFlagrun_v1_2017jul import ZooPolicyTensorflow as PolHumanoid2
    # Flagrun and Harder is compatible with normal Humanoid in observations and actions.

    possible_participants = [
        ("Synthtraining Walker2d-v1", PolWalker),
        ("Synthtraining Hopper-v1",   PolHopper),
        ("Synthtraining HalfCheetah-v1", PolHalfCheetah),
        ("Synthtraining Humanoid-v1", PolHumanoid1),
        ("Synthtraining Humanoid-v1", PolHumanoid2),
        ]
    env_id, PolicyClass = possible_participants[ np.random.randint(len(possible_participants)) ]
    env = lab.make(env_id)
    env.unwrapped.multiplayer(env, game_server_guid=sys.argv[1], player_n=int(sys.argv[2]))

    pi = PolicyClass("mymodel", env.observation_space, env.action_space)

    while 1:
        obs = env.reset()
        while 1:
            a = pi.act(obs, None)
            obs, rew, done, info = env.step(a)
            if done: break
