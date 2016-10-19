# Changelog

## 2016.3

The following features and changes in behavior are introduced in this version:

* Default to using ```/var/lib/fedora-atomic``` instead of ```/srv/fedora-atomic```
  ([6b6ecf18](https://github.com/fedora-infra/fedmsg-atomic-composer/commit/6b6ecf18)).
* Return the ref and commitid of the composed tree at the end
  ([#7](https://github.com/fedora-infra/fedmsg-atomic-composer/pull/7)).


The 2016.3 release contains the following bug fixes:

* ```--new-chroot``` is now only used with rpm-ostree and not with mock
  ([#4](https://github.com/fedora-infra/fedmsg-atomic-composer/issues/4)).
* ```/var/tmp``` is used for the temporary working directory instead of ```/tmp```
  ([544d7091](https://github.com/fedora-infra/fedmsg-atomic-composer/commit/544d7091)).
