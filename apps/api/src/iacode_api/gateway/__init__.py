"""The application's side of the Model Gateway: its stores and its composition.

The gateway package itself is provider-neutral and knows nothing about this application. This
package is where the two are joined: PostgreSQL implementations of the gateway's ports, and the
function that builds a gateway from the application's typed settings.
"""
