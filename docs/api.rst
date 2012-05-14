.. _ref-api:

========
REST API
========

.. http://127.0.0.1:8000/api/v1/
.. http://127.0.0.1:8000/api/v1/page/
.. http://127.0.0.1:8000/api/v1/page/:name/
.. http://127.0.0.1:8000/api/v1/page/:name/?section=:section
.. http://127.0.0.1:8000/api/v1/page/:name/?format=:format
.. http://127.0.0.1:8000/api/v1/page/:name/section/
.. http://127.0.0.1:8000/api/v1/page/:name/section/:id/


Creating a page
===============

.. code-block:: bash

    curl -i -H "Content-Type: application/json" -X PUT -d '{"content": "Hello world"}' -u username:password http://localhost:8000/api/v1/page/Index/

.. code-block:: http

    HTTP/1.0 201 CREATED
    Date: Sat, 12 May 2012 23:52:59 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: text/html; charset=utf-8
    Location: http://localhost:8000/api/v1/page/Index/

or

.. code-block:: bash

    curl -i -H "Content-Type: application/json" -X POST -d '{"name": "Another_page", "content": "Here comes some content"}' -u username:password http://localhost:8000/api/v1/page/

.. code-block:: http

    HTTP/1.0 201 CREATED
    Date: Sat, 12 May 2012 23:56:39 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: text/html; charset=utf-8
    Location: http://localhost:8000/api/v1/page/Another_page/


Getting a page
==============


.. code-block:: bash

    curl -i -H "Accept: application/json" -X GET http://localhost:8000/api/v1/page/Index/

.. code-block:: http

    HTTP/1.0 200 OK
    Date: Sun, 13 May 2012 00:11:51 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: application/json; charset=utf-8

    {
        "content": "Hello world",
        "name": "Index"
    }


Updating a page
===============

.. code-block:: bash

    curl -i -H "Content-Type: application/json" -X PUT -d '{"content": "Hello universe."}' -u username:password http://localhost:8000/api/v1/page/Index/

.. code-block:: http

    HTTP/1.0 204 NO CONTENT
    Date: Sun, 13 May 2012 00:03:38 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 0
    Content-Type: text/html; charset=utf-8

or

.. code-block:: bash

    curl -i -H "Content-Type: application/json" -X PATCH -d '{"content": "Hello world, hello universe."}' -u username:password http://localhost:8000/api/v1/page/Index/

.. code-block:: http

    HTTP/1.0 202 ACCEPTED
    Date: Sun, 13 May 2012 00:04:48 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: text/html; charset=utf-8


Listing all the pages
=====================

.. code-block:: bash

    curl -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/v1/page/

or more simply

.. code-block:: bash

    curl -i http://127.0.0.1:8000/api/v1/page/

.. code-block:: http

    HTTP/1.0 200 OK
    Date: Sun, 13 May 2012 00:18:21 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: application/json; charset=utf-8

    {
        "meta": {
            "limit": 20, 
            "next": null, 
            "offset": 0, 
            "previous": null, 
            "total_count": 2
        }, 
        "objects": [
            {
                "content": "Hello world, hello universe.", 
                "name": "Index"
            }, 
            {
                "content": "Here comes some content", 
                "name": "AnotherPage"
            }
        ]
    }

Deleting a page
===============

.. code-block:: bash

    curl -i -X DELETE -u username:password http://localhost:8000/api/v1/page/Index/

.. code-block:: http

    HTTP/1.0 204 NO CONTENT
    Date: Sun, 13 May 2012 00:06:20 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Length: 0
    Content-Type: text/html; charset=utf-8


