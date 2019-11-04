package command

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"os/user"
	"path"
	"strings"

	"github.com/urfave/cli"
)

var (
	copyPath string
)

func init() {
	usr, err := user.Current()
	if err != nil {
		panic(err)
	}
	copyPath = path.Join(usr.HomeDir, ".mygo-copy")
}

func AddCopyCommand() cli.Command {
	return cli.Command{
		Name:   "copy",
		Usage:  "Copy any text",
		Action: copy,
	}
}

func AddPasteCommand() cli.Command {
	return cli.Command{
		Name:   "paste",
		Usage:  "Paste text after copy command",
		Action: paste,
	}
}

func copy(c *cli.Context) error {
	var text string
	if c.NArg() > 0 {
		text = strings.Join(c.Args(), " ")
	} else {
		return errors.New("Require text argument")
	}
	fmt.Printf("Copying \"%v\"\n", text)
	return ioutil.WriteFile(copyPath, []byte(text), 0755)
}

func copyText(text string) error {
	f, err := os.OpenFile(copyPath, os.O_WRONLY|os.O_CREATE, 0755)
	if err != nil {
		return err
	}
	if _, err := f.WriteString(text); err != nil {
		return err
	}
	if err := f.Close(); err != nil {
		return err
	}
	return nil
}

func paste(c *cli.Context) error {
	text := ""
	if fileExists(copyPath) {
		b, err := ioutil.ReadFile(copyPath)
		if err != nil {
			return err
		}
		text = string(b)
	}
	fmt.Println(text)
	return nil
}
