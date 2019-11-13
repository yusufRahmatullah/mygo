package main

import (
	"os"

	"github.com/urfave/cli"
	"github.com/yusufRahmatullah/mygo/command"
)

const (
	version = "0.2.0"
)

func main() {
	app := cli.NewApp()
	app.Name = "MyGo"
	app.Usage = "Simple Utility for daily tasks"
	app.Version = version
	app.Commands = []cli.Command{
		command.AddGitStatusCommand(),
		command.AddGenCommand(),
		command.AddCopyCommand(),
		command.AddPasteCommand(),
		command.AddHrCommand(),
	}
	err := app.Run(os.Args)
	if err != nil {
		panic(err)
	}
}
