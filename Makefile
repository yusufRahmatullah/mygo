build: check
	go build -o mygo main.go
check:
	gocyclo -over 5 .
clean:
	go clean
	rm -f mygoc
compress: clean build
	upx --brute -o mygoc mygo
install-linux: compress
	sudo mv -f mygoc /usr/local/bin/mygo
	ls -hl /usr/local/bin/mygo
