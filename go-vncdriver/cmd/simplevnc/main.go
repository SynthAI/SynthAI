package main

import (
	"log"
	"os"
	"runtime/pprof"
	"time"

	"github.com/synthai/go-vncdriver/labvnc"
)
import _ "net/http/pprof"

type foo struct {
	bar string
}

func main() {
	f, err := os.Create("/tmp/profile-tight.pprof")
	if err != nil {
		panic(err)
	}
	pprof.StartCPUProfile(f)
	defer pprof.StopCPUProfile()

	labvnc.ConfigureLogging()

	batch := labvnc.NewVNCBatch()
	err = batch.Open("conn", labvnc.VNCSessionConfig{
		// Address:          "127.0.0.1:5900",
		Address:          "3.public-devbox.sci.synthai-tech.com:20000",
		Password:         "synthai",
		Encoding:         "tight",
		FineQualityLevel: 100,
	})
	if err != nil {
		panic(err)
	}

	start := time.Now()
	updates := 0
	errs := 0
	for i := 0; i < 200000; i++ {
		elapsed := time.Now().Sub(start)
		if elapsed >= time.Duration(1)*time.Second {
			delta := float64(elapsed / time.Second)
			log.Printf("Received: updates=%.2f errs=%.2f", float64(updates)/delta, float64(errs)/delta)

			start = time.Now()
			updates = 0
			errs = 0
		}

		batchEvents := map[string][]labvnc.VNCEvent{
			"conn": []labvnc.VNCEvent{},
		}
		_, updatesN, errN := batch.Step(batchEvents)
		if errN["conn"] != nil {
			log.Fatalf("error: %+v", errN["conn"])
		}

		updates += len(updatesN["conn"])
		time.Sleep(16 * time.Millisecond)
	}

	// f, err := os.Create("/tmp/hi.prof")
	// if err != nil {
	//     log.Fatal("could not create memory profile: ", err)
	// }
	// runtime.GC() // get up-to-date statistics
	// if err := pprof.WriteHeapProfile(f); err != nil {
	//     log.Fatal("could not write memory profile: ", err)
	// }
	// f.Close()
}
