build: check
	go build -o my main.go
check:
	gocyclo -over 5 .
clean:
	go clean
	rm -f myc
compress: clean build
	upx --brute -o myc my
install-linux: compress
	sudo mv -f myc /usr/local/bin/my
	ls -hl /usr/local/bin/my
