#!/bin/bash -x
PACKAGE=fedmsg-atomic-composer
VERSION=`grep ^Version rpm/$PACKAGE.spec | cut -d: -f2 | tr -d ' '`
RELEASE=`grep ^Release rpm/$PACKAGE.spec | cut -d: -f2 | cut -d% -f1 | tr -d ' '`
python setup.py sdist --format=bztar && \
mv dist/* ~/rpmbuild/SOURCES/ && \
cp rpm/*.spec ~/rpmbuild/SPECS/ && \
rpmbuild -ba ~/rpmbuild/SPECS/$PACKAGE.spec && \
sudo rpm -e $PACKAGE{,-consumer} ; \
sudo rpm -vih ~/rpmbuild/RPMS/noarch/$PACKAGE{,-consumer}-$VERSION-$RELEASE.*.noarch.rpm
#ansible-playbook -v ansible/playbook.yml
