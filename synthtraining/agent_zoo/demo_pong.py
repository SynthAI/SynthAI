import os, sys, subprocess
import numpy as np
import lab
import synthtraining 

def play(env, pi, video):
    episode_n = 0
    while 1:
        episode_n += 1
        obs = env.reset()
        if video: video_recorder = lab.monitoring.video_recorder.VideoRecorder(env=env, base_path=("/tmp/demo_pong_episode%i" % episode_n), enabled=True)
        while 1:
            a = pi.act(obs)
            obs, rew, done, info = env.step(a)
            if video: video_recorder.capture_frame()
            if done: break
        if video: video_recorder.close()
        break

if len(sys.argv)==1:
    import synthtraining .multiplayer
    game = synthtraining .lab_pong.PongSceneMultiplayer()
    gameserver = synthtraining .multiplayer.SharedMemoryServer(game, "pongdemo", want_test_window=True)
    for n in range(game.players_count):
        subprocess.Popen([sys.executable, sys.argv[0], "pongdemo", "%i"%n])
    gameserver.serve_forever()

else:
    player_n = int(sys.argv[2])

    env = lab.make("Synthtraining Pong-v1")
    env.unwrapped.multiplayer(env, game_server_guid=sys.argv[1], player_n=player_n)

    from Synthtraining Pong_v0_2017may1 import SmallReactivePolicy as Pol1
    from Synthtraining Pong_v0_2017may2 import SmallReactivePolicy as Pol2
    if player_n==0:
        pi = Pol1(env.observation_space, env.action_space)
    else:
        pi = Pol2(env.observation_space, env.action_space)
    play(env, pi, video=False)   # set video = player_n==0 to record video

