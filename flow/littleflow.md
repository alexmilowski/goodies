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


## Operations

An operation acts upon the data received on its input ports and produces data on its output ports.  While many operations act as a filter and only have a single input and output port, operations can have any number of input ports and any number of output ports.

Operations may take parameters that are values passed at invocation.  Parameters differ from input ports in that their values are effectively computed once and passed to any invocation of the operation no matter where it runs.  If an operation is replicated or parallelized in any way, the parameter value will be same regardless of where and when the operation is executed.

Each parameter is declared positionally, has a name, and may have a default value.  When parameters have a default value they may be omitted upon invocation.  For example, `mytask(1,2,key='name')` has two positional parameters `1` and `2` and a parameter named `key` with the value `name`.  Positional parameters must occur before any keyword parameters.

Each operation's signature must be provided for the flow to be constructed.  While an implementation is free to provide built-in operations, a flow may declare an operation's signature.  For example, an the `add-property` operation from the previous section:

```
declare operation [ json ] add-property(name : string, value) [ json ]
```

While operations are similar to function declarations, they separate input ports from invocation parameters.  This distinction is important in what flows between operations may cross system boundaries or the operation map be run in parallel (e.g., via map/reduce) while the invocation parameters are values that are computed, possibly once, and passed to the operation no matter where it runs.

The operation name and parameters is preceded by the input port declarations and is followed by the output port declarations.  Each of these port declarations is contained in square brackets.  The operation parameterts are declared much like function parameters with types and default values.

A port declaration set of ports giving the names, optional types, and order.  For example:

```
[ json, text : string ]
```

declares two ports, the first one named `json` and a second one named `text` with an expected value of a string.

Ports may accept multiple values and their cardinality can be specified as a singleton, one or more (+), or zero or more (*):

```
[ documents : *, values : string+]
```

Types and cardinality are simple annotations to the port.  An implementation is not required to check either types or cardinality.  See [the section on typing](#typing) for more information.

The order of the ports is significant only when binding inputs invocation expressions.  Otherwise, ports are referred to by their names.

Similarly, parameters to operations are declared except that they are allowed to have default values.  The default value is always specified as a literal whose lexical value can be interpreted by the operation as the expected type.

```
declare operation [] range(max : int = '10') [ numbers : int+]
```

## Operators

### Chain Operator

### Append Operator

## Flows

A flow puts everything together.  The most basic flow just declares custom operations and various chains.

```
flow version = '1.0';

<metadata.json> → if (' data["@type"]==="Person" ')
                  then add-property(name='name',value='Alex')
                  else add-property(name='author',value='Alex')
                  ≫ <enhanced-metadata.json>
```

In the above flow, the inputs and outputs are bound to particular resources.  We can make the flow more general by using named pipes:


```
flow version = '1.0'

in → if (' data["@type"]==="Person" ')
     then add-property(name='name',value='Alex')
     else add-property(name='author',value='Alex')
     ≫ out
```

The named port `in` becomes a source and the named port `output` becomes a sink.  The overall flow now requires an input to be specified and produces an output that can be bound by the invocation.

The above example has a particular signature.  If we want to re-use that flow within another flow as an operation, we can give it a name:

```
flow version = '1.0';

declare flow [ in ] enhance() [out] {

in → if (' data["@type"]==="Person" ')
     then add-property(name='name',value='Alex')
     else add-property(name='author',value='Alex')
     ≫ output
}

<metadata.json> → enhance() ≫ <enhanced-metadata.json>
     
```

Finally, we can import flows and operation declarations as a library:

```
flow version = '1.0';

import <mylib.flow>;

<metadata.json> → enhance() ≫ <enhanced-metadata.json>
```


## Expressions


## Typing

## Grammar

*`operation-decl`* `:=` `'declare' 'operation'` *`input-port-decl`*`?` *`name`*`'('` *`parameter`*  `')'` *`output-port-decl`*`?` `';'`

*`input-port-decl`* `:=` *`port-decl`*

*`output-port-decl`* `:=` *`port-decl`*

*`port-decl`* `:=` 


