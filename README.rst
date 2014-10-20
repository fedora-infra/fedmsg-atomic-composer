fedmsg-ostree-composer
======================

Triggers rpm-ostree composes when Fedora updates/rawhide/branched
repositories are updated.

Running
-------

.. code-block:: bash

   sudo yum install fedmsg-hub
   sudo cp config.py /etc/fedmsg.d/ostreecomposer.py
   python setup.py egg_info
   PYTHONPATH=$(pwd) fedmsg-hub
