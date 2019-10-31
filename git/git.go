package git

import (
	"fmt"
	"os/exec"
	"strings"
)

type Git struct {
}

func (git *Git) Branch() (string, error) {
	return cmd("git rev-parse --abbrev-ref HEAD")
}

func (git *Git) Repo() (string, error) {
	return cmd("git remote get-url origin")
}

func (git *Git) PrintStatus() error {
	branch, err := git.Branch()
	if err != nil {
		return err
	}
	sm, err := git.Status()
	if err != nil {
		return err
	}
	fmt.Println("On Branch", branch)
	for k, v := range sm {
		fmt.Println(k)
		for _, f := range v {
			fmt.Println("\t", f)
		}
		fmt.Println("")
	}
	return nil
}

func (git *Git) Status() (map[string][]string, error) {
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
		d := strings.Split(line, " ")
		key := d[0]
		arr, ok := statusMap[key]
		if ok {
			arr = append(arr, d[1])
		} else {
			statusMap[key] = []string{d[1]}
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
