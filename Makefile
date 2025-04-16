DEB_BUILD_DIR := build/deb

.PHONY: all deb clean

all: deb

deb:
	mkdir -p $(DEB_BUILD_DIR)
	dpkg-buildpackage -us -uc -b -rfakeroot
	mv ../bkang_*.deb ../bkang_*.buildinfo ../bkang_*.changes $(DEB_BUILD_DIR)/

clean_deb:
	rm -rf $(DEB_BUILD_DIR)
	rm -Rf debian/.debhelper/
	rm debian/bkang.debhelper.log debian/bkang.substvars debian/bkang.postinst.debhelper debian/bkang.prerm.debhelper

clean: clean_deb
	rm -rf build
	rm -rf debian/bkang_*.buildinfo debian/bkang_*.changes debian/bkang_*.deb
	rm -rf debian/*.debhelper debian/*.substvars debian/*.tar.xz
	rm -rf debian/*.buildinfo debian/*.changes debian/*.deb
	rm -rf debian/*.install debian/*.dirs debian/*.links
	rm -rf debian/*.ex debian/*.EX debian/*.log
	rm -rf *.tar.xz *.tar.gz *.tar.bz2 *.tar.lzma *.tar.zst *.tar.lzo *.tar.lz4 *.tar.zstd *.tar.zlib
	
