.. _ogcapi-records:

Publishing metadata to OGC API - Records
========================================

`OGC API - Records`_ provides geospatial data access functionality to vector data.

To add vector data to pygeoapi, you can use the dataset example in :ref:`configuration`
as a baseline and modify accordingly.

Providers
---------

pygeoapi core record providers are listed below, along with a matrix of supported query
parameters.

.. csv-table::
   :header: Provider, properties (filters), resulttype, q, bbox, datetime, sortby, properties (display), domains, CQL, transactions
   :align: left

   `ElasticsearchCatalogue`_,✅,results/hits,✅,✅,✅,✅,✅,✅,✅,✅
   `TinyDBCatalogue`_,✅,results/hits,✅,✅,✅,✅,❌,✅,✅,✅
   `CSWFacade`_,✅,results/hits,✅,✅,✅,✅,❌,✅,❌,❌


Below are specific connection examples based on supported providers.

Connection examples
-------------------

ElasticsearchCatalogue
^^^^^^^^^^^^^^^^^^^^^^
.. note::
   Requires Python packages elasticsearch and elasticsearch-dsl

.. note::
   Elasticsearch 8 or greater is supported.


To publish an Elasticsearch index, the following are required in your index:

* indexes must be documents of valid `OGC API - Records GeoJSON Features`_
* index mappings must define the GeoJSON ``geometry`` as a ``geo_shape``

.. code-block:: yaml

   providers:
       - type: record
         name: ElasticsearchCatalogue
         data: http://localhost:9200/some_metadata_index
         id_field: identifier
         time_field: datetimefield

The ES provider also has the support for the CQL queries as indicated in the table above.

.. seealso::
  :ref:`cql` for more details on how to use Common Query Language (CQL) to filter the collection with specific queries.

TinyDBCatalogue
^^^^^^^^^^^^^^^

.. note::
   Requires Python package tinydb

To publish a TinyDB index, the following are required in your index:

* indexes must be documents of valid `OGC API - Records GeoJSON Features`_

.. code-block:: yaml

   providers:
       - type: record
         editable: true|false  # optional, default is false
         name: TinyDBCatalogue
         data: /path/to/file.db
         id_field: identifier
         time_field: datetimefield

CSWFacade
^^^^^^^^^

.. note::
   Requires Python package `OWSLib`_

To publish a CSW using pygeoapi, the CSW base URL (`data`) is required.  Note that the
CSW Record core model is supported as a baseline.

.. code-block:: yaml

   providers:
       - type: record
         name: CSWFacade
         data: https://demo.pycsw.org/cite/csw
         id_field: identifier
         time_field: datetime
         title_field: title


Metadata search examples
------------------------

* overview of record collection

  * http://localhost:5000/collections/metadata-records
  
* queryables

  * http://localhost:5000/collections/foo/queryables
  
* queryables on specific properties

  * http://localhost:5000/collections/foo/queryables?properties=title,type

* queryables with current domain values

  * http://localhost:5000/collections/foo/queryables?profile=actual-domain

* queryables on specific properties with current domain values

  * http://localhost:5000/collections/foo/queryables?profile=actual-domain&properties=title,type

* browse records

  * http://localhost:5000/collections/foo/items
  
* paging

  * http://localhost:5000/collections/foo/items?offset=10&limit=10
  
* CSV outputs

  * http://localhost:5000/collections/foo/items?f=csv
  
* query records (spatial)

  * http://localhost:5000/collections/foo/items?bbox=-180,-90,180,90
  
* query records (attribute)

  * http://localhost:5000/collections/foo/items?propertyname=foo
  
* query records (temporal)

  * http://localhost:5000/collections/my-metadata/items?datetime=2020-04-10T14:11:00Z
  
* query features (temporal) and sort ascending by a property (if no +/- indicated, + is assumed)

  * http://localhost:5000/collections/my-metadata/items?datetime=2020-04-10T14:11:00Z&sortby=datetime
  
* query features (temporal) and sort descending by a property

  * http://localhost:5000/collections/my-metadata/items?datetime=2020-04-10T14:11:00Z&sortby=-datetime
  
* fetch a specific record

  * http://localhost:5000/collections/my-metadata/items/123
  

.. note::
   provider `id_field` values support slashes (i.e. ``my/cool/identifier``). The client request would then
   be responsible for encoding the identifier accordingly (i.e. ``http://localhost:5000/collections/my-metadata/items/my%2Fcool%2Fidentifier``)

.. _`OGC API - Records`: https://ogcapi.ogc.org/records
.. _`OGC API - Records GeoJSON Features`: https://raw.githubusercontent.com/opengeospatial/ogcapi-records/master/core/openapi/schemas/recordGeoJSON.yaml
.. _`OWSLib`: https://geopython.github.io/OWSLib
