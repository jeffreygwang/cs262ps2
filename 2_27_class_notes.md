# Lecture 9: Time I

## Unit Tests
- Test the basic units of code
    - Individual functions / methods / procedures
    - Feed inputs, check outputs
- Lots of case: expected cases, edge cases, etc.
- If units call out other units, you should mock up objects through configuration
    - But you should have base pieces of code that you can test individually
- They are *not* end-to-end and don't test integration with other programs

## Time
> Asynchronous vs Synchronous systems really reflect how sequences of events occur

The core notion is one of **causation** helps you figure out the sequences of events. Single process programming, even with multiple threads, can be stepped through (although you might encounter a [heisenbug](https://en.wikipedia.org/wiki/Heisenbug)).

Multiple processes are more difficult; multiple processes on different machines is even harder.

Most OS'es do not assign time to individual instructions, meaning multiple instructions will occur between any 2 timestamps on the wall clock.

> The CPU's are sometimes so large that you can't propagate the clock signal across the entire signal in the time it took for the next chip action to occur.

## Distributed Systems State

Event ordering basically describes something that respects causality.

## Clock Properties

If e causally precedes e', C(e) < C(e')

## Logical Clocks

Lamport's notion. Each process has a clock that gives a value for each event.

Consecutive events e and e' have C(e) = C(e') + 1.

Communications between processes are labelled with a timestamp.

If you are communicating between different processes, and P1 has consecutive events e and e', and P2 receives event e' at time T:

C_{P2}(e') = max(C_{P2}(e), T) + 1

> In other words, if one person is behind, they re-shift their clock up when receiving another event from a different process. If you receive an event with an old timestamp, you update it to your current.

If two processes never communicate, their events will be concurrent. However, if they do communicate, you get snapshotting of states.

### A somewhat hacky algorithm for snapshotting state

Consider some set of machines with corresponding processes, 1 per machine. If I wish to get a snapshot of everyone's state at a given moment, I will send everyone a directive "send me all of your internal state (stack machine concept) at some impossibly high timestamp in the future that no one could be at."

Then, I send that timestamp to everyone. At that instance, everyone's clocks get synced forward to that timestamp, and everyone sends me their internal state at a single time point.

That timestamp defines an **epoch**.

> This timestamping is really important because not using it could cause a violation in causality. Here's an example. Let's say I send a message to B and C asking them to send my state. But because of a network delay, C sends his state, then sends B a message, then B gets my message, and B sends her state containing that message from C that doesn't exist in my records.

## Vector Clocks

Each process keeps a vector of logical clocks for all processes.

VC(e_i)[i] += 1 if e_i is internal or a send

VC(e_i)[i] = max(VC, TS(m)) += 1 for each index if e_i is a receive

In a vector clock, each process maintains a vector of integers that represents its local clock. It's initialized as <0 0 ... 0 0> and when an event occurs, the entry for that process is incremeneted in the vector.

When a process receives an event with a vector timestamp, it compares the vector timestamp to its own vector clock to determine the causal relationship between the events.

If the vector timestamp indicates that the sending process has already processed an event from a particular process that the receiving process has not yet processed, then **the receiving process knows that the received event is causally related to the unprocessed event.**

In this way, vector clocks enable a partial ordering of events that takes into account the causal relationships between events.

> **There seems to be good readings this lecture.**

## Design Assignment #2

Build a scale model of a simple dist. system with systems at different speeds. 3 processes; diff instructions/second on each process; send messages sometimes (sometimes 1 or 2); sometimes look for messages.

Figure out some way of watching what happens with the message queues; keep a notebook to experiment with things.

Should be 3 separate processes (talking over sockets probably).

