package labvnc

import "github.com/synthai/go-vncdriver/vncclient"

type Renderer interface {
	Init(width, height uint16, name string, screen []vncclient.Color) error
	Apply(colors []*vncclient.FramebufferUpdateMessage)
	Render()
	Close() error
}
