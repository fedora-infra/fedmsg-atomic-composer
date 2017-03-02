# Changelog

## 2017.2.0

This is a bugfix release, with the following commits:

* AtomicConsumer now has a config key
  ([5e32653f](https://github.com/fedora-infra/fedmsg-atomic-composer/commit/5e32653f)).
* stderr messages are now logged at info and not error level
  ([eba7e334](https://github.com/fedora-infra/fedmsg-atomic-composer/commit/eba7e334)).
* Set enabled to 1 in repo.mako
  ([1b51be98](https://github.com/fedora-infra/fedmsg-atomic-composer/commit/1b51be98)).
* Explicity install ostree in the mock config
  ([fd58aee1](https://github.com/fedora-infra/fedmsg-atomic-composer/commit/fd58aee1)).
* Enable CAP_NET_ADMIN for systemd-nspawn in the mock config
  ([#19](https://github.com/fedora-infra/fedmsg-atomic-composer/pull/19)).

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
* Log files are now closed during cleanup
  ([#9](https://github.com/fedora-infra/fedmsg-atomic-composer/pull/9)).
