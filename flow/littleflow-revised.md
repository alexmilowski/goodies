# A little flow language

## A brief introduction

Workflows are tasks that occur within some set of relationships. That
is, a workflow forms a graph where the nodes are tasks and the edges are the
relationships. The relationships in the graph provide ordering of which tasks
occur in what order by the preceding tasks they may depend upon and other
criteria (e.g., conditionals).

By the nature, *workflows are not DAGs* as some have cycles and partitions. As
such, in this context, a workflow is a graph that:

 1. Every node represents a task in the workflow.
 1. Every edge is a directed edge.
 1. For any two distinct nodes A and B, there is only a single directed edge from A to B.

With this definition, a few observations:

 * Nodes are not required to be connected.
 * A workflow can consist of disconnected subgraphs
 * Cycles are allowed

A workflow is performed over time. As such, a workflow generates a DAG of the trace of the execution. At each point in time that a task is performed, the instance of task as certain number of incoming edges from preceding tasks is followed by a certain number of following tasks. This is called the **execution trace**.

A workflow is a *flow* of information from task to the next. The preceding tasks have state and side effects. In actuality, a side effect is usually an artifact (e.g., a document or action taking in the "real world"). These side effects are typically the record and objective of the workflow; things that are the eventual outcome when finished.

The state is something specific to the workflow being execute. Between tasks there is information, metadata, that can be passed along. This metadata may be important and dictate how subsequent task operate and the cardinality of the
operations they perform.

As such, over the edge flows information. Each task receives inputs over incoming edges and outputs information over outgoing edges. This information provides subsequent tasks the ability to evaluate what and whether they can perform their own task.

## What are tasks?

While conceptually a task can be anything:

 * a computational task over the inputs and product outputs without side-effects
 * a process whose arguments are the inputs, affect the state of the world by producing some number of artifacts, and producing metadata over its outputs
 * a invocation of the "real world" affect the state of objects, interacting with people, and generating artifacts or metadata over task outputs

Concretely, a task is invoked by a workflow engine that feeds the task various inputs and receives various outputs. Once complete, the engine determines the next step in computation and feeds outputs to inputs. That is, tasks are "black boxes" with metadata inputs and outputs.

## Technical foundation

A flow represents a workflow as a graph that:

 1. Nodes represent tasks.
 1. Edges are directed.
 1. An edge from A to B means that A occurs before B.
 1. Two distinct nodes A and B are only connected by one edge from A to B.

A sequence of structured information flows between nodes over directed edges. A task may choose how to interpret such information from all incoming edges.

Information flowing between tasks can be limited to structured information that can be represented in a JSON [1] data format. The sequences can then be represented in a JSON-seq [2] format.

A task:

 * receives inputs, possibly empty, over incoming edges
 * produces outputs, possibly empty, over outgoing edges
 * may create side-effects

A *side effect* is typically an artifact or change in state of the world. For example, a task may write data to database, notify a user, or invoke actions in the physical world.

Within the workflow itself, only the data flowing over the edges is explicitly know by each task. Task writers by choose to convey information via the data flow or via side effects.

A task in a workflow is not a replacement for a general purpose programming language. To avoid complexity, there is a single sequence of inputs and single sequence of outputs. Every connected task receives the same input sequence.

## A syntax for workflows

The goals of this syntax are:

 1. A compact representation of the workflow graph
 1. A representation of tasks and their metadata operations
 1. Enabling common expressions over metadata between tasks (e.g., conditionals)

The graph is constructed with a single arrow operator (i.e., '→' U+2192 or '->') to connect two tasks.

A task is identified by name which are alpha-numberic along with the hyphen ('-') and underscore ('_') (e.g. my-task)

A task may have parameters indicated by keyword/value pairs within parenthesis (e.g. range(start=1,end=10)).

A workflow is a sequence of whitespace separated statements. Each statement starts with a label or task name, a sequence of arrow operations, and ends with a label or task name.

A label is a colon prefixed name.

A flow statement is a sequence of arrow operations:

```
transform → inference → store
```

Two different flow statements can be combined with a label:

```
transform → :transformed
:transformed → inference → store(name='outcome.json')
:transformed → store(name='source.json')
```

The workflow graph has meets where two or more outputs may converge on a single task. These are represented by different statements:

```
A → C
B → C
```

More complex graphs may require labeling a particular edge to attached another task outcome:

```
A :meet → C → D → E
B → :meet
```

The start of a flow statement can be a label:

```
:before → A → B → C
```

And the end of a flow statement can also be a label:

```
A → B → C → :after
```

Labels only have a syntactic meaning.

A resource by a URI reference in angle brackets:

```
<dataset.json> → inference → store
```

This has a consequence of loading the resource as the output of a the task.

Finally, it can be useful to qualify whether a task should occur rather than have the decision within the task itself. Within a statement, the 'when' expression enables conditional subgraphs:

```
A → if .status==0 then B
    else C
```

The expression language is jsonpath [3]. The consequence of a conditional is a task invocation.

## Stitching the graph

The workflow graph is stitched together from all instances of tasks with the same parameters. For example, these are distinct task invocations:

 * `C(name='albert')`
 * `C(name='eve')`

While this workflow refers to the same invocation of task 'C':

```
A → C(name='bob')
B → C(name='bob')
```

which is equivalent to:

```
A :meet → C(name='bob')
B → :meet
```

Stitching becomes more complicated with conditionals. Conditionals generate an implicit task-like node.

Consider:

```
A → if .status==0 then B
    else C → :outcome
:outcome → D
```

The possible execution traces are:

```
A → B → D
A → C → D
```

But the graph is really:

```
A → B|C → D
```

## First and last tasks

Any task in a workflow has preceding tasks (those from incoming edges) and following tasks (those connected to outgoing edges). Assuming a left-is-preceding orientation, the left-most tasks are those without any preceding task and the right most is those without any following tasks.

The label `:start` is a reserved label for all the left-most tasks.

The label `:end` is a reserved label for all the right-most tasks.

Thus, the workflow:

```
A → B → C
D → E
F → B
```

is equivalent to:

```
:start → A → B → C → :end
:start → D → E → :end
:start → F → B
```

## Task definitions

A task is referred to by name and invoked with simple parameter values. As such, it is not necessary to declare a task. An implementation can determine the set of names and parameters used.

Within an implementation, the actual task definition may be far more complicated and implementation specific. That definition is out of scope for this specification.

A implementation can identify the tasks referred, the parameters used (and not used), and match the invocation to expected definitions and constraints. Subsequently, it can raise errors as necessary.


## Task inputs and outputs

A task receives a set of inputs of structured information. If a preceding task produces no output or there is no preceding tasks, the input is a singleton empty object (i.e., `{}`). Similarly, if a task produces no explicit output upon completion, it defaults to produce a singleton empty object.

A task may output more than one structured object as its output (e.g., a sequence of numbers, vectors, objects, etc.).

When two tasks are joined (e.g. `A → B`), the input is simply the output of the preceding task.

If there are more than two incoming edges, the following rules are applied:

 1. All singleton empty objects are equivalent and merged into a single empty object.
 1. If a non-empty object is present, singleton empty objects are omitted.
 2. If multiple inputs are present, the union of all the non-empty objects is the input.

In short, inputs are merged into a single sequence of structured objects with duplicate empty objects merged or omitted when non-empty objects are present.
