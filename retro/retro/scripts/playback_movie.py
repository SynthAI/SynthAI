#!/usr/bin/env python
import argparse
import csv
import json
import numpy as np
import os
import retro
import signal
import socket
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor as Executor


def playback_movie(emulator, movie, monitor_csv=None, video_file=None, info_file=None, npy_file=None, viewer=None, video_delay=0, lossless=None):
    ffmpeg_proc = None
    viewer_proc = None
    info_steps = []
    actions = np.empty(shape=(0, emulator.NUM_BUTTONS), dtype=bool)
    if viewer or video_file:
        video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        video.bind(('127.0.0.1', 0))
        audio.bind(('127.0.0.1', 0))
        vr = video.getsockname()[1]
        ar = audio.getsockname()[1]
        stdout = None
        output = []
        input_vformat = ['-r', str(emulator.em.get_screen_rate()), '-s', '%dx%d' % emulator.observation_space.shape[1::-1], '-pix_fmt', 'rgb24', '-f', 'rawvideo']
        input_aformat = ['-ar', '%i' % emulator.em.get_audio_rate(), '-ac', '2', '-f', 's16le']
        if video_file:
            if not lossless:
                output = ['-c:a', 'aac', '-b:a', '128k', '-strict', '-2', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-f', 'mp4', '-pix_fmt', 'yuv420p', video_file]
            elif lossless == 'mp4':
                output = ['-c:a', 'aac', '-b:a', '192k', '-strict', '-2', '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '0', '-f', 'mp4', '-pix_fmt', 'yuv444p', video_file]
            elif lossless == 'mp4rgb':
                output = ['-c:a', 'aac', '-b:a', '192k', '-strict', '-2', '-c:v', 'libx264rgb', '-preset', 'veryslow', '-crf', '0', '-f', 'mp4', '-pix_fmt', 'rgb24', video_file]
            elif lossless == 'png':
                output = ['-c:a', 'flac', '-c:v', 'png', '-pix_fmt', 'rgb24', '-f', 'matroska', video_file]
            elif lossless == 'ffv1':
                output = ['-c:a', 'flac', '-c:v', 'ffv1', '-pix_fmt', 'bgr0', '-f', 'matroska', video_file]
        if viewer:
            stdout = subprocess.PIPE
            output = ['-c', 'copy', '-f', 'nut', 'pipe:1']
        ffmpeg_proc = subprocess.Popen(['ffmpeg', '-y',
                                        *input_vformat, '-probesize', '32', '-thread_queue_size', '10000', '-i', 'tcp://127.0.0.1:%i?listen' % vr,  # Input params (video)
                                        *input_aformat, '-probesize', '32', '-thread_queue_size', '60', '-i', 'tcp://127.0.0.1:%i?listen' % ar,  # Input params (audio)
                                        *output],  # Output params
                                       stdout=stdout)
        video.close()
        audio.close()
        video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audio_connected = False

        time.sleep(0.2)
        video.connect(('127.0.0.1', vr))
        if viewer:
            viewer_proc = subprocess.Popen([viewer, '-'], stdin=ffmpeg_proc.stdout)
    frames = 0
    score = 0
    wasDone = False

    def killprocs(*args, **kwargs):
        ffmpeg_proc.terminate()
        if viewer:
            viewer_proc.terminate()
            viewer_proc.wait()
        raise BrokenPipeError

    while movie.step():
        keys = []
        for i in range(emulator.NUM_BUTTONS):
            keys.append(movie.get_key(i))
        if npy_file:
            actions = np.vstack((actions, (keys,)))
        display, reward, done, info = emulator.step(keys)
        if info_file:
            info_steps.append(info)
        score += reward
        frames += 1
        try:
            if hasattr(signal, 'SIGCHLD'):
                signal.signal(signal.SIGCHLD, killprocs)
            if viewer_proc and viewer_proc.poll() is not None:
                break
            if ffmpeg_proc and frames > video_delay:
                sound = emulator.em.get_audio()
                video.sendall(bytes(display))
                if not audio_connected:
                    time.sleep(0.2)
                    audio.connect(('127.0.0.1', ar))
                    audio_connected = True
                if len(sound):
                    audio.sendall(bytes(sound))
        except BrokenPipeError:
            break
        finally:
            if hasattr(signal, 'SIGCHLD'):
                signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        if done and not wasDone:
            if monitor_csv:
                monitor_csv.writerow({'r': score, 'l': frames, 't': frames / 60.0})
            frames = 0
            score = 0
        wasDone = done
    if hasattr(signal, 'SIGCHLD'):
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    if monitor_csv and frames:
        monitor_csv.writerow({'r': score, 'l': frames, 't': frames / 60.0})
    if npy_file:
        kwargs = {
            'actions': actions
        }
        if info_file:
            kwargs['info'] = info_steps
        try:
            np.savez_compressed(npy_file, **kwargs)
        except IOError:
            pass
    elif info_file:
        try:
            with open(info_file, 'w') as f:
                json.dump(info_steps, f)
        except IOError:
            pass
    if ffmpeg_proc:
        video.close()
        audio.close()
        if not viewer_proc or viewer_proc.poll() is None:
            ffmpeg_proc.wait()


def load_movie(movie_file):
    movie = retro.Movie(movie_file)
    duration = -1
    while movie.step():
        duration += 1
    movie = retro.Movie(movie_file)
    movie.step()
    emulator = retro.make(game=movie.get_game(), state=retro.STATE_NONE, use_restricted_actions=retro.ACTIONS_ALL)
    data = movie.get_state()
    emulator.initial_state = data
    emulator.reset()
    return emulator, movie, duration


def _play(movie, args, monitor_csv):
    video_file = None
    info_file = None
    if args.lossless in ('png', 'ffv1'):
        ext = '.mkv'
    else:
        ext = '.mp4'

    emulator, m, duration = load_movie(movie)
    if args.ending is not None:
        delay = duration - args.ending
    else:
        delay = 0
    basename = os.path.splitext(movie)[0]
    if not args.no_video:
        video_file = basename + ext
    if args.info_dict:
        info_file = basename + '.json'
    if args.npy_actions:
        npy_file = basename + '.npz'
    playback_movie(emulator, m, monitor_csv, video_file, info_file, npy_file, args.viewer, delay, args.lossless)
    del emulator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('movies', type=str, nargs='+')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--jobs', '-j', type=int, default=1)
    group.add_argument('--csv-out', '-c', type=str)
    parser.add_argument('--ending', '-e', type=int)
    parser.add_argument('--viewer', '-v', type=str)
    parser.add_argument('--no-video', '-V', action='store_true')
    parser.add_argument('--info-dict', '-i', action='store_true')
    parser.add_argument('--npy-actions', '-a', action='store_true')
    parser.add_argument('--lossless', '-L', type=str, choices=['mp4', 'mp4rgb', 'png', 'ffv1'])
    args = parser.parse_args()
    monitor_csv = None
    monitor_file = None
    if args.csv_out:
        game = retro.Movie(args.movies[0]).get_game()
        monitor_file = open(args.csv_out, 'w')
        monitor_file.write('#{"t_start": 0.0, "lab_version": "lab_retro", "env_id": "%s"}\n' % game)
        monitor_csv = csv.DictWriter(monitor_file, fieldnames=['r', 'l', 't'])
        monitor_csv.writeheader()

    with Executor(args.jobs) as pool:
        list(pool.map(_play, *zip(*[(movie, args, monitor_csv) for movie in args.movies])))
    if monitor_file:
        monitor_file.close()


if __name__ == '__main__':
    main()