"""The application's binding to the shared system of record.

The declarative base, the domain model and the engine helpers live in ``packages/persistence``,
because the Temporal worker reads the same tables and two ORM definitions of one schema drift. This
package is what binds them to *this* process: :mod:`iacode_api.db.engine` turns the API's typed
:class:`~iacode_api.config.Settings` into the four values the shared engine takes, and nothing else
here redefines a table.
"""
