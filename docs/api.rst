REST API
========

http://127.0.0.1:8000/api/v1/
http://127.0.0.1:8000/api/v1/page/
http://127.0.0.1:8000/api/v1/page/:name/
http://127.0.0.1:8000/api/v1/page/:name/?section=:section
http://127.0.0.1:8000/api/v1/page/:name/?format=:format
http://127.0.0.1:8000/api/v1/page/:name/section/
http://127.0.0.1:8000/api/v1/page/:name/section/:id/


List all the pages
------------------

.. code-block:: bash
    $ curl -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/v1/page/
    HTTP/1.0 200 OK
    Date: Mon, 30 Apr 2012 05:12:58 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: application/json; charset=utf-8
    {
        meta: {
            limit: 20,
            next: null,
            offset: 0,
            previous: null,
            total_count: 0
        },
        objects: []
    }

Create a new page
-----------------

.. code-block:: bash
    $ curl -i -H "Content-Type: application/json" -X PUT -d '{"content": "Hello World"}' http://localhost:8000/api/v1/page/Hello_world/ -u foo:bar 
    HTTP/1.0 201 CREATED
    Date: Mon, 30 Apr 2012 05:11:56 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: text/html; charset=utf-8
    Location: http://localhost:8000/api/v1/page/6/

or

.. code-block:: bash
    $ curl -i -H "Content-Type: application/json" -X POST -d '{"name": "bar", "content": "content2"}' http://localhost:8000/api/v1/page/ -u foo:bar
    HTTP/1.0 201 CREATED
    Date: Mon, 30 Apr 2012 05:09:21 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: text/html; charset=utf-8
    Location: http://localhost:8000/api/v1/page/5/

Update a page
-------------

.. code-block:: bash
    $ curl -i -H "Content-Type: application/json" -X PATCH -d '{"content": "Hello World3"}' http://localhost:8000/api/v1/page/Hello_world2/ -u foo:bar                                                                               
    HTTP/1.0 202 ACCEPTED
    Date: Mon, 30 Apr 2012 05:15:47 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Content-Type: text/html; charset=utf-8
