# A Little Flow Language

## A Brief Introduction

A data flow (or 'flow' for short) is a set of operations on data connected by pipes over which data flows.  Each operation has a set of input and output ports to and from which connections can be made by pipes.  The resulting flow is a graph where the edges are pipes between operations.

An operation in a flow is something that manipiulates its inputs to produce a set of outputs.  This operation may be simple task of adding a property to a JSON object or a more complex task like making an API request to a web server.  At minimum, an operation in a flow must have its input ports connected to something that produces data whereas outputs can be left unattached.

The overal goal of the syntax of the language is to describe the data flow and enabled modularization.  We start by allowing brief chain of manipulations that use the arrow operator (i.e., '→' U+2192 or '->') to connect operations and the append operator (i.e., '≫' U+226B or '>>') to store the result.

```
<metadata.json> → add-property(name='author',value='Alex')
                → add-property(name='subject',value='data flow')
                ≫ <enhanced-metadata.json>
```

On the left we start with the input URI surrounded by angle brackets (i.e., '<' and '>') and we end with the output URI.  Inbetween we chain together two operations to manipulate the input document by adding a author and 'subject' property value.

Underneath, we a simple graph of source resource `metadata.json` , two operations involving `add-property`, and an output resource `enhanced-metadata.json` that are connected by pipes.  Data flows from the source resource, through each operation, and out to the output resource.  The `add-property` operation in the example has a simple filter signature that has one input port and output port with two parameters for the name and value of the property to add.

At the end, the append operator '≫' stores the result to the output resource.  Without the append operator, the chain executes but the result is not stored and available after the flow execution.

More complex chains can involve branching with conditional:

```
<metadata.json> → if (' data["@type"]==="Person" ')
                  then add-property(name='name',value='Alex')
                  else add-property(name='author',value='Alex')
                ≫ <enhanced-metadata.json>
```

Instead of an operation, we have a conditional.  The expression is evaluated in the default expression langauge for the flow (i.e., JavaScript).  Based on the outcome, the conditional executes one of two branches as part of the chain and then continues the flow.  The conditional acts as a guard that guarantees that one one of the chains will execute.

Finally, some flows are not straight chains of operations.  Instead of a resource, a named pipe can be used to refer to the output from a chain of operations.  That named pipe can be used as the input to start another chain.

```
<metadata.json> → add-property(name='name',value='Alex') ≫ enhanced
enhanced ≫ <enhanced-metadata.json>
enhanced → query-duplicates(href='http://example.io/services/duplicates') ≫ <alternatives.json>
```

In the example, the enhanced metadata is stored in the output resource `enhanced-metadata,json` and the result of checking for duplicates is stored in the output resource `alternatives.json`.

In all the examples, we have refered to operations as if they already exist with particular signatures for inputs ports, parameters, and outputs ports.  A flow engine can prepopulate the operations with variety implementations  from native-langauge (e.g., JavaScript, Python, etc.) implementations that accept the inputs and produce the outputs.  All the flow needs is a declaration of the signature.

```
declare operation [ json ] add-property(name : string, value) [ json ];
```

While operations are similar to function declarations, they separate input ports from invocation parameters.  This distinction is important in what flows between operations may cross system boundaries or the operation map be run in parallel (e.g., via map/reduce) while the invocation parameters are values that are computed, possibly once, and passed to the operation no matter where it runs.

The operation name and parameters is preceded by the input port declarations and is followed by the output port declarations.  Each of these port declarations is contained in square brackets.  The operation parameterts are declared much like function parameters with types and default values.
