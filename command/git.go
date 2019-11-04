package command

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strings"

	"github.com/urfave/cli"
)

const (
	DefaultKnownPath = "known_gs.txt"
	GitAdded         = "Git-added"
	NotGit           = "Not git-added"
	Untracked        = "Untracked"
)

var (
	knownFile string
)

type git struct {
	branch    string
	knownFile string
	knownList []string
	statusMap map[string][]string
}

func newGit(knownFile string) (*git, error) {
	g := &git{knownFile: knownFile}
	if err := g.readKnownList(); err != nil {
		return nil, err
	}
	if err := g.getBranch(); err != nil {
		return nil, err
	}
	if err := g.readStatusMap(); err != nil {
		return nil, err
	}
	return g, nil
}

func (g *git) getBranch() error {
	if branch, err := cmd("git rev-parse --abbrev-ref HEAD"); err == nil {
		g.branch = branch
		return nil
	} else {
		return err
	}
}

func (g *git) readKnownList() error {
	var path string
	if fileExists(g.knownFile) {
		path = g.knownFile
	} else if fileExists(DefaultKnownPath) {
		path = DefaultKnownPath
	} else {
		g.knownList = []string{}
		return nil
	}
	f, err := ioutil.ReadFile(path)
	if err != nil {
		return err
	}
	g.knownList = strings.Split(string(f), "\n")
	return nil
}

func (g *git) readStatusMap() error {
	out, err := cmd("git status -s")
	if err != nil {
		return err
	}
	g.statusMap = extractStatusMap(g.knownList, strings.Split(out, "\n"))
	return nil
}

func AddGitStatusCommand() cli.Command {
	gsc := cli.Command{
		Name:   "gs",
		Usage:  "Simplified git status",
		Action: gitStatus,
	}
	gsc.Flags = []cli.Flag{
		cli.StringFlag{
			Name: "known-files, k",

			Value: "known_gs.txt",
			Usage: "List of known files that will not be shown",
		},
	}
	return gsc
}

func gitStatus(c *cli.Context) error {
	knownFile := c.String("known-files")
	g, err := newGit(knownFile)
	if err != nil {
		return err
	}
	ctn := []string{fmt.Sprintf("On Branch %v", g.branch)}
	for _, key := range []string{NotGit, GitAdded, Untracked} {
		if v, ok := g.statusMap[key]; ok {
			ctn = append(ctn, extendStatus(key, v)...)
		}
	}
	fmt.Println(strings.Join(ctn, "\n"))
	return nil
}

func extractStatusMap(knownList []string, lines []string) map[string][]string {
	statusMap := make(map[string][]string)
	for _, line := range lines {
		if line == "" {
			continue
		}
		key, file := extractStatus(line)
		if stringInSlice(file, knownList) {
			continue
		}
		arr, ok := statusMap[key]
		if ok {
			statusMap[key] = append(arr, file)
		} else {
			statusMap[key] = []string{file}
		}
	}
	return statusMap
}

func cmd(command string) (string, error) {
	cmds := strings.Split(command, " ")
	bin := cmds[0]
	args := cmds[1:]
	out, err := exec.Command(bin, args...).Output()
	if err != nil {
		return "", err
	}
	return string(out), nil
}

func extendStatus(key string, value []string) []string {
	ctn := []string{fmt.Sprintf("%v:", key)}
	for _, v := range value {
		ctn = append(ctn, fmt.Sprintf("\t%v", v))
	}
	return ctn
}

func extractStatus(line string) (string, string) {
	work := string(line[1])
	f := string(line[3:])
	key := "Git-added"
	if work == "?" {
		key = "Untracked"
	} else if work != " " {
		key = "Not git-added"
	}
	return key, f
}

func fileExists(filepath string) bool {
	_, err := os.Stat(filepath)
	if os.IsNotExist(err) {
		return false
	}
	return true
}

func readKnownList(knownPath string) ([]string, error) {
	var path string
	if fileExists(knownPath) {
		path = knownPath
	} else if fileExists(DefaultKnownPath) {
		path = DefaultKnownPath
	} else {
		return []string{}, nil
	}
	f, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}
	return strings.Split(string(f), "\n"), nil
}

func stringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}
