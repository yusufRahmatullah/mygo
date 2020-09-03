build: check
	go build -o my main.go
check: dep-test
	gocyclo -over 5 .
clean:
	go clean
	rm -f myc
dep:
	go mod download
dep-test:
	go get github.com/fzipp/gocyclo
compress: clean build
	upx --brute -o myc my
install-linux: compress
	sudo mv -f myc /usr/local/bin/my
	ls -hl /usr/local/bin/my
install-windows: compress
	mv -f myc /d/portable/gobin/my
	ls -hl /d/portable/gobin/my
