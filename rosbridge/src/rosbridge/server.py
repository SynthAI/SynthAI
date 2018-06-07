"""
Defines a class LabProxyZmqServer that listens on a zmq port, creates an environment as requested over the port,
and accepts step & reset calls on that environment.
Usage:
    def make_env(env_name):
        if env_name == 'MyRemoteEnv':
            return MyRemoteEnv(...)
    s = LabProxyZmqServer(url, make_env)
    s.run_main()
As a special bonus, if you run this module directly:
  python lab/envs/proxy/server.py tcp://127.0.0.1:6911
it will serve all the Lab environments over zmq at tcp://127.0.0.1:6911
"""
import math, random, time, logging, re, base64, argparse, collections, sys, os, traceback, threading
import numpy as np
import ujson
import zmq, zmq.utils.monitor
import lab
import zmq_serialize

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LabProxyZmqServer(object):
    def __init__(self, url, make_env):
        self.url = url
        self.make_env = make_env
        self.env = None
        self.env_name = None
        self.session_id = None
        self.session_last_use = 0.0
        self.session_owner = None
        self.log_msgs = []

        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.REP)
        self.sock.bind(self.url)
        self.monitor_sock = self.sock.get_monitor_socket()
        self.rpc_lock = threading.Lock()
        self.rpc_rd = threading.Condition(self.rpc_lock)
        self.monitor_thr = threading.Thread(target = self.run_monitor)
        self.monitor_thr.daemon = True
        self.monitor_thr.start()

        self.timeout_thr = threading.Thread(target = self.run_timeout)
        self.timeout_thr.daemon = True
        self.timeout_thr.start()

    def run_main(self):
        logger.info('zmq lab server running on %s', self.url)
        while True:
            rx = self.sock.recv_multipart(flags=0, copy=True, track=False)
            logger.debug('%s > %s', self.url, rx[0])
            rpc = zmq_serialize.load_msg(rx)
            with self.rpc_lock:
                self.handle_rpc(rpc)

    def run_monitor(self):
        logger.info('zmq lab server listening on monitoring socket')
        while True:
            ev = zmq.utils.monitor.recv_monitor_message(self.monitor_sock)
            logger.debug('Monitor Event %s', ev)
            with self.rpc_lock:
                if ev['event'] == zmq.EVENT_DISCONNECTED:
                    logger.info('zmq disconnect')
                elif ev['event'] == zmq.EVENT_ACCEPTED:
                    logger.info('zmq accept')

    def run_timeout(self):
        while True:
            with self.rpc_lock:
                if self.session_id is not None and time.time() - self.session_last_use > 3.0:
                    self.close_env()
                    self.session_last_use = 0.0
                    self.session_id = None
                    self.session_owner = None
            time.sleep(1)

    def close_env(self):
        if self.env is not None and hasattr(self.env, 'save_logs'):
            log_url = self.env.save_logs()
            if log_url is not None:
                self.log_to_client('See high-res traces at %s' % log_url)
        self.env_name = None
        if self.env is not None:
            self.env.close()
        self.env = None
        self.session_id = None
        self.session_owner = None
        self.session_last_use = 0.0
        logger.info('LabProxyZmqServer closed')

    def log_to_client(self, msg):
        self.log_msgs.append(msg)

    def handle_rpc(self, rpc):
        rpc_method = rpc.get('method', None)
        rpc_params = rpc.get('params', None)

        def reply(rpc_result, rpc_error=None):
            tx = zmq_serialize.dump_msg({
                'result': rpc_result,
                'error': rpc_error,
                'log_msgs': self.log_msgs,
            })
            del self.log_msgs[:]
            logger.debug('%s < %s', self.url, tx[0])
            self.sock.send_multipart(tx, flags=0, copy=False, track=False)

        try:
            if rpc_method == 'step':
                reply(self.handle_step(rpc_params))
            elif rpc_method == 'reset':
                reply(self.handle_reset(rpc_params))
            elif rpc_method == 'setup':
                reply(self.handle_setup(rpc_params))
            elif rpc_method == 'close':
                reply(self.handle_close(rpc_params))
            elif rpc_method == 'render':
                reply(self.handle_render(rpc_params))
            else:
                raise Exception('unknown method %s' % rpc_method)
        except:
            ex_type, ex_value, ex_tb = sys.exc_info()
            traceback.print_exception(ex_type, ex_value, ex_tb)
            reply(None, str(ex_type) + ': ' + str(ex_value))

    def check_session(self, params):
        session_id = params['session_id']
        if session_id == self.session_id:
            self.session_last_use = time.time()
        else:
            raise Exception('Wrong session id. Expected %s, got %s' % (str(self.session_id), str(session_id)))

    def handle_reset(self, params):
        self.check_session(params)
        obs = self.env.reset()
        return {
            'obs': obs,
            'session_id': self.session_id,
        }

    def handle_step(self, params):
        self.check_session(params)
        action = params['action']
        obs, reward, done, info = self.env.step(action)
        return {
            'obs': obs,
            'reward': reward,
            'done': done,
            'info': info,
            'session_id': self.session_id,
        }

    def handle_setup(self, params):
        if self.session_id is not None:
            raise Exception('Robot in use by %s' % str(self.session_owner))

        self.env = self.make_env(params['env_name'])
        if self.env is None:
            raise Exception('No such environment')
        self.env_name = params['env_name']
        self.session_id = zmq_serialize.mk_random_cookie()
        self.session_last_use = time.time()
        self.session_owner = params.get('session_owner', 'unknown')
        logger.info('Creating env %s. session_id=%s owner=%s', self.env_name, self.session_id, self.session_owner)

        return {
            'observation_space': self.env.observation_space,
            'action_space' : self.env.action_space,
            'reward_range': self.env.reward_range,
            'session_id': self.session_id,
        }

    def handle_close(self, params):
        if self.session_id is not None:
            self.check_session(params)
        prev_session_id = self.session_id
        self.close_env()
        return {
            'session_id': prev_session_id,
        }

    def handle_render(self, params):
        self.check_session(params)
        mode = params['mode']
        close = params['close']
        img = self.env.render(mode, close)
        return {
            'img': img,
            'session_id': self.session_id,
        }


if __name__ == '__main__':
    server_url = sys.argv[1]
    zmqs = LabProxyZmqServer(server_url, lab.make)
    zmqs.run_main()
