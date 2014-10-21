#!/bin/sh
python setup.py sdist --format=bztar
mv dist/* ~/rpmbuild/SOURCES/
cp rpm/*.spec ~/rpmbuild/SPECS/
rpmbuild -ba ~/rpmbuild/SPECS/fedmsg-atomic-composer.spec
