fedmsg-koji-consumer
====================

An example of using `fedmsg <http://fedmsg.com>`_ to monitor `koji <http://koji.fedoraproject.org>`_, the `Fedora <http://fedoraproject.org>`_ Build System.

Running
-------

.. code-block:: bash

   sudo yum install fedmsg-hub
   sudo cp config.py /etc/fedmsg.d/kojiconsumer.py
   python setup.py egg_info
   PYTHONPATH=$(pwd) fedmsg-hub
