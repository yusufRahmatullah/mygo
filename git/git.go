package git

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strings"
)

const (
	DefaultKnownPath = "known_gs.txt"
	GitAdded         = "Git-added"
	NotGit           = "Not git-added"
	Untracked        = "Untracked"
)

type Git struct {
}

func (git *Git) Branch() (string, error) {
	return cmd("git rev-parse --abbrev-ref HEAD")
}

func (git *Git) Push() error {
	_, err := cmd("git push origin HEAD")
	return err
}

func (git *Git) Repo() (string, error) {
	return cmd("git remote get-url origin")
}

func (git *Git) PrintStatus(knownPath string) error {
	knownList, err := readKnownList(knownPath)
	if err != nil {
		return err
	}
	branch, err := git.Branch()
	if err != nil {
		return err
	}
	sm, err := git.Status(knownList)
	if err != nil {
		return err
	}
	ctn := []string{fmt.Sprintf("On Branch %v", branch)}
	for _, key := range []string{NotGit, GitAdded, Untracked} {
		if v, ok := sm[key]; ok {
			ctn = append(ctn, extendStatus(key, v)...)
		}
	}
	fmt.Println(strings.Join(ctn, "\n"))
	return nil
}

func (git *Git) Status(knownList []string) (map[string][]string, error) {
	out, err := cmd("git status -s")
	if err != nil {
		return nil, err
	}
	statusMap := make(map[string][]string)
	lines := strings.Split(out, "\n")
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
	return statusMap, nil
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
