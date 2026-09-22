"""The API's binding to the agent runtime.

The runtime is a library. This package composes it for the request-serving process: the declared
profiles, the store over the shared schema, and the service that creates and reads runs. Executing
a run is not here — that is the Temporal worker's, and the only thing the API does about execution
is start the workflow and signal it.
"""
