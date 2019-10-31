package main

import (
	"fmt"
	"os"

	"github.com/akamensky/argparse"
	"github.com/yusufRahmatullah/mygo/git"
)

var (
	g = &git.Git{}
)

func main() {
	parser := argparse.NewParser("mygo", "Simple utility for daily tasks")
	gsCmd := parser.NewCommand("gs", "Simplified git status")
	gpCmd := parser.NewCommand("gp", "Git push current branch")
	err := parser.Parse(os.Args)
	if err != nil {
		print(parser.Usage(err))
		return
	}
	if gsCmd.Happened() {
		gs()
	} else if gpCmd.Happened() {
		gp()
	} else {
		print("Something went wrong")
	}
}

func gp() {
	err := g.Push()
	handleErr(err)
}

func gs() {
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
