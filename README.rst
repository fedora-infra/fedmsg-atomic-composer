fedmsg-atomic-composer
======================

Triggers `Atomic <http://projectatomic.io>`_ ostree composes when Fedora
updates/rawhide/branched repositories are updated.

Build
-----

.. code-block:: bash

   ./build.sh

Deploy
------

.. code-block:: bash

   ansible-playbook --ask-sudo-pass ansible/playbook.yml

Monitor
-------

.. code-block:: bash

   journalctl -f -u fedmsg-atomic-composer -u atomic-compose\*


Triggering locally
------------------

.. code-block:: bash

   fedmsg-logger --modname 'bodhi' --topic 'updates.fedora.sync' --message='{"release": "21", "repo": "updates"}' --json-input
   fedmsg-logger --modname 'compose' --topic 'rawhide.rsync.complete' --message='{"arch":"x86_64"}' --json-input
   fedmsg-logger --modname 'compose' --topic 'branched.rsync.complete' --message='{"arch":"x86_64"}' --json-input
