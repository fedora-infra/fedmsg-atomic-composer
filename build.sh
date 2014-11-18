#!/bin/bash -x
python setup.py sdist --format=bztar && \
mv dist/* ~/rpmbuild/SOURCES/ && \
cp rpm/*.spec ~/rpmbuild/SPECS/ && \
rpmbuild -ba ~/rpmbuild/SPECS/fedmsg-atomic-composer.spec && \
sudo rpm -e fedmsg-atomic-composer{,-consumer} ; \
sudo rpm -vih ~/rpmbuild/RPMS/noarch/fedmsg-atomic-composer{,-consumer}-0.0.1-2.fc21.noarch.rpm && \
ansible-playbook -v ansible/playbook.yml
