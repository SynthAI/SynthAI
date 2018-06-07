zbar-0.10:
	curl -OL https://downloads.sourceforge.net/project/zbar/zbar/0.10/zbar-0.10.tar.bz2
	# Check the SHA
	shasum -c zbar-0.10.tar.bz2.sha
	tar xf zbar-0.10.tar.bz2
	rm zbar-0.10.tar.bz2

zbar-0.10.tar.bz2.sha:
	curl -OL https://downloads.sourceforge.net/project/zbar/zbar/0.10/zbar-0.10.tar.bz2
	shasum -a 256 zbar-0.10.tar.bz2 > zbar-0.10.tar.bz2.sha
	rm zbar-0.10.tar.bz2
