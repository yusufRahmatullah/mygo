package command

import (
	"fmt"

	"github.com/urfave/cli"
)

func AddHrCommand() cli.Command {
	return cli.Command{
		Name:    "hr",
		Aliases: []string{"sep"},
		Usage:   "Print a separator",
		Action:  sep,
	}
}

func sep(c *cli.Context) error {
	fmt.Println(`
################################
#                              #
#         My Separator         #
#                              #
################################
	`)
	return nil
}
