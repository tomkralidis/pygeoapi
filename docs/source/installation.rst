.. _install:

Install
=======

pygeoapi is easy to install on numerous environments.  Whether you are a user, administrator or developer, below
are multiple approaches to getting pygeoapi up and running depending on your requirements.

Requirements and dependencies
-----------------------------

pygeoapi runs on Python 3.

.. note::

   The exact Python version requirements are aligned with the version of Python on the pygeoapi supported Ubuntu
   operating system version.  For example, as of 2024-07, the supported version of Python is bound to Ubuntu 22.04
   (Jammy) which supports Python 3.10.  Ensure you have a Python version that is compatible with the current Ubuntu
   version that is specified in pygeoapi's `Dockerfile`_.

Core dependencies are included as part of a given pygeoapi installation procedure.  More specific requirements
details are described below depending on the platform.


For developers and the truly impatient
--------------------------------------

.. code-block:: bash

   python3 -m venv pygeoapi
   cd pygeoapi
   . bin/activate
   git clone https://github.com/geopython/pygeoapi.git
   cd pygeoapi
   pip3 install --upgrade pip
   pip3 install -r requirements.txt
   python3 setup.py install
   cp pygeoapi-config.yml example-config.yml
   vi example-config.yml  # edit as required
   export PYGEOAPI_CONFIG=example-config.yml
   export PYGEOAPI_OPENAPI=example-openapi.yml
   pygeoapi openapi generate $PYGEOAPI_CONFIG --output-file $PYGEOAPI_OPENAPI
   pygeoapi serve
   curl http://localhost:5000


.. note::

   If you get this error: `ModuleNotFoundError: No module named 'setuptools'`, it is because `setuptools` 
   is not installed on your system. Although some Python installers will install it, `setuptools` is `not part of the Python standard library <https://docs.python.org/3/py-modindex.html#cap-s>`_. 
   See this `guide <https://packaging.python.org/en/latest/guides/installing-using-linux-tools/>`_ to install it in your system.

pip
---

`PyPI package info <https://pypi.org/project/pygeoapi>`_

.. code-block:: bash

   pip3 install pygeoapi

Docker
------

Using DockerHub
^^^^^^^^^^^^^^^

`DockerHub image`_

.. code-block:: bash

   docker pull geopython/pygeoapi:latest
   
Using GitHub Container Registry   
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`GCHR image`_

.. code-block:: bash

   docker pull ghcr.io/geopython/pygeoapi:latest   

Kubernetes
----------

.. note:: 
   If using the PostgreSQL feature provider it is recommended to set NGINX ingress affinity-mode to persistent; see the below ingress example. 

.. code-block:: bash
   
   ---
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
   name: ${KUBE_NAMESPACE}
   labels:
      app: ${KUBE_NAMESPACE}
   annotations:
      nginx.ingress.kubernetes.io/affinity: "cookie"
      nginx.ingress.kubernetes.io/session-cookie-name: ${KUBE_NAMESPACE}
      nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
      nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
      nginx.ingress.kubernetes.io/ssl-redirect: "false"
      nginx.ingress.kubernetes.io/affinity-mode: persistent
      nginx.ingress.kubernetes.io/session-cookie-hash: sha1
   spec:
   ingressClassName: nginx
   rules:
   - host: ${APP_HOSTNAME}
      http:
         paths:
         - path: /
         pathType: Prefix
         backend:
            service:
               name: ${KUBE_NAMESPACE}
               port:
               number: ${CONTAINER_PORT}


Conda
-----

`Conda package info <https://anaconda.org/conda-forge/pygeoapi>`_

.. code-block:: bash

   conda install -c conda-forge pygeoapi

UbuntuGIS
---------

`UbuntuGIS package (stable) <https://launchpad.net/%7Eubuntugis/+archive/ubuntu/ppa/+sourcepub/10758317/+listing-archive-extra>`_

`UbuntuGIS package (unstable) <https://launchpad.net/~ubuntugis/+archive/ubuntu/ubuntugis-unstable/+sourcepub/10933910/+listing-archive-extra>`_

.. code-block:: bash

   apt-get install python3-pygeoapi

FreeBSD
-------

`FreeBSD port <https://www.freshports.org/graphics/py-pygeoapi>`_

.. code-block:: bash

   pkg install py-pygeoapi


Summary
-------
Congratulations!  Whichever of the abovementioned methods you chose, you have successfully installed pygeoapi
onto your system.


.. _`DockerHub image`: https://hub.docker.com/r/geopython/pygeoapi
.. _`GCHR image`: https://github.com/geopython/pygeoapi/pkgs/container/pygeoapi
.. _`Dockerfile`: https://github.com/geopython/pygeoapi/blob/master/Dockerfile
