package main

import (
	"fmt"
	"os"

	"github.com/akamensky/argparse"
	"github.com/yusufRahmatullah/mygo/git"
)

func main() {
	parser := argparse.NewParser("mygo", "Simple utility for daily tasks")
	gitCmd := parser.NewCommand("gd", "Advance git diff")
	err := parser.Parse(os.Args)
	if err != nil {
		print(parser.Usage(err))
		return
	}
	if gitCmd.Happened() {
		gd()
	} else {
		print("Something went wrong")
	}
}

func gd() {
	g := &git.Git{}
	err := g.PrintStatus()
	handleErr(err)
}

func handleErr(err error) {
	if err != nil {
		panic(err)
	}
}

func print(a ...interface{}) {
	fmt.Println(a...)
}
