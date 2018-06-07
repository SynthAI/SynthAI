This command reads in an FBS 1.2 file (SynthAI-specific format) of messages sent
from a server to a client in a VNC session. It transcodes FramebufferUpdate
messages from their original encoding to an equivalent message with raw
encoding.

`Dockerfile` defines a tiny docker image that contains only the `transcode`
executable. The resulting image is about 6MB.

Use the image like so:

```
$ cd out/demo/<path-to-demos>
$ docker run -v $(pwd):/tmp docker.synthai.com/transcode -in=/tmp/server.fbs.orig -out=/tmp/transcoded.fbs
```

It is recommended to first `mv` the tight-encoded `server.fbs` file to `server.fbs.orig` to keep track of the original demo.