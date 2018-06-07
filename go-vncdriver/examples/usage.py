import go_vncdriver
import time

from PIL import Image

from lab.envs.classic_control import rendering

# res = go_vncdriver.example(1, 2)
# res = go_vncdriver.connect(["hi", "tester"])
# import ipdb;ipdb.set_trace()

go_vncdriver.setup()
h = go_vncdriver.VNCSession(["localhost:5900"], None)
print(h.remotes)

viewer = rendering.SimpleImageViewer()
while True:
    observation, info = h.flip()
    if any(i['vnc.updates.n'] for i in info):
        for ob in observation:
            viewer.imshow(ob)
            # Image.fromarray(ob).show()
            # print(ob.shape)
    time.sleep(1/10)

h.close()
