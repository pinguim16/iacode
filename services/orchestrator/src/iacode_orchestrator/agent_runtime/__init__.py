"""The worker's half of the agent runtime: the activities and the durable workflow.

`iacode_agent_runtime` owns the behaviour and declares its ports. This package supplies them inside
the Temporal worker: the activities are the ports' implementations, and the workflow is the driver
that calls the engine with those activities behind it.

The split is what keeps the workflow deterministic. Workflow code is replayed from history, so a
database read, a clock call or a model call inside it would produce a different answer on replay and
corrupt the run. Every one of them is an activity here, and the loop that decides *which* activity
to run next is pure arithmetic over the plan.
"""
