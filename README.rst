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
