package command

import (
	"fmt"

	"github.com/urfave/cli"
	"github.com/yusufRahmatullah/gopass"
	"golang.org/x/crypto/ssh/terminal"
)

func AddGenCommand() cli.Command {
	gc := cli.Command{
		Name:  "gen",
		Usage: "Generate Password or Pin",
		Subcommands: []cli.Command{
			{
				Name:   "pass",
				Usage:  "Generate password",
				Action: genPass,
			},
			{
				Name:   "pin",
				Usage:  "Generate pin",
				Action: genPin,
			},
		},
	}
	return gc
}

func genBase() (string, error) {
	print("Master key: ")
	master, err := terminal.ReadPassword(0)
	if err != nil {
		return "", err
	}
	println("")
	print("Purpose: ")
	purpose, err := terminal.ReadPassword(0)
	if err != nil {
		return "", err
	}
	println("")
	return fmt.Sprintf("%v::%v", string(master), string(purpose)), nil
}

func genPass(c *cli.Context) error {
	seed, err := genBase()
	if err != nil {
		return err
	}
	pass := gopass.GenPass(seed)
	println("Password:", pass)
	return nil
}

func genPin(c *cli.Context) error {
	seed, err := genBase()
	if err != nil {
		return err
	}
	pin := gopass.GenPin(seed)
	println("Pin:", pin)
	return nil
}
