fedmsg-atomic-composer
======================

Triggers `Atomic <http://projectatomic.io>`_ ostree composes when Fedora
updates/rawhide/branched repositories are updated.

You can also trigger composes via a command-line tool or Python API.

Features
--------

 * Dynamic atomic treefile generation
 * Dynamic yum repo configuration generation
 * Dynamic mock configuration generation
 * Efficient mock chroot management
 * fedmsg-consumer that can trigger composes when new repos are available
 * Python API
 * CLI

Bootstrap
---------

.. code-block::

   sudo yum -y install git rpmdevtools python-{devel,mock} ansible
   rpmdev-setuptree


Configure
---------

All of the configuration lives in the `config.py` in JSON format. You can
define all of your releases like so:

.. code-block:: bash

   config = dict(
        releases={
            'f21-updates': {
                'name': 'f21-updates',
                'repo': 'updates',
                'version': '21',
                'arch': 'x86_64',

                # Here you define your OSTree `treefile.json <https://github.com/projectatomic/rpm-ostree/blob/master/doc/treefile.md>`_
                'tree': 'docker-host',
                'treefile': {
                    'include': 'fedora-atomic-docker-host.json',
                    'ref': 'fedora-atomic/f21/x86_64/updates/docker-host',
                    'repos': ['fedora-21', 'updates'],
                    'selinux': False,
                },

                # The name of the mock chroot to build and maintain
                'mock': 'fedora-21-updates-x86_64',

                # The git branch to use in the `git_repo` for the parent
                # treefile & repo configurations
                'git_branch': 'f21',

                # Add or overwrite yum repository name:urls. This lets you 
                # compose trees against your own repositories.
                'repos': {},
            }, …


Composing a tree via the CLI
----------------------------

.. code-block:: bash

   sudo -iu rpmostreecompose fedmsg-atomic-composer-cli f21-updates-testing


Using the Python API
--------------------

To compose a tree via the Python API, all you need to do is pass the
:meth:`compose` method a `release` dictionary from the `config.py`.

.. code-block:: python

   from fedmsg_atomic_composer.composer import AtomicComposer
   from fedmsg_atomic_composer.config import config

   release = config['releases']['f21-updates']
   composer = AtomicComposer()
   result = composer.compose(release)


Build & Deploy locally
----------------------

.. code-block:: bash

   ./build.sh

Enable & Monitor the fedmsg consumer
------------------------------------

.. code-block:: bash

   systemctl enable fedmsg-atomic-composer
   systemctl start fedmsg-atomic-composer
   journalctl -f -u fedmsg-atomic-composer

Triggering locally via fedmsg
-----------------------------

.. code-block:: bash

   fedmsg-logger --modname 'bodhi' --topic 'updates.fedora.sync' --message='{"release": "21", "repo": "updates"}' --json-input
   fedmsg-logger --modname 'compose' --topic 'rawhide.rsync.complete' --message='{"arch":"x86_64"}' --json-input
   fedmsg-logger --modname 'compose' --topic 'branched.rsync.complete' --message='{"arch":"x86_64"}' --json-input
