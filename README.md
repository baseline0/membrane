# cyprus

A membrane-computing oriented programming language

## Overview

Cyprus is a programming language based on the concept of a [P System](http://en.wikipedia.org/wiki/P_system).

Computation is modeled as chemical reactions happening within protocellular
constructions, producing new chemicals.

## Why Membrane Computing?

### For Insurance & Regulatory Architecture

Membrane systems (P-systems) naturally model **hierarchical regulatory domains** and **distributed compliance rules**:
- Nested membrane structures mirror multi-level regulatory frameworks (federal → provincial → enterprise policies)
- Bio-inspired parallelism enables efficient constraint satisfaction across rule hierarchies
- Architecture tested against conventional optimization algorithms (genetic algorithms, particle swarm optimization, fuzzy inference)

### For AI & Research Architecture

This repository represents a **novel approach to constraint satisfaction and optimization**:
- Alternative algorithm class for problems where neural networks or classical methods plateau
- Research-to-practice pipeline: theory → implementation → reproducible benchmarks
- Quantum-ready architecture: P-systems have natural mappings to quantum computing models (see `docs/quantum/`)

### Evolution from Research

This work extends academic research on fuzzy clustering and pattern recognition (Ph.D., U of Manitoba) into membrane computing—bridging distributed systems modeling with emerging quantum computing approaches.

**Try it yourself:**
```bash
uv run malta run 1          # Run a built-in simulation
uv run malta benchmark toy  # Run convergence analysis
```

## Malta: ML Algorithm Benchmarking Framework

The **Malta framework** benchmarks P-systems against conventional ML optimization algorithms using standard test suites:

- **Algorithms:** Genetic Algorithms, Particle Swarm Optimization, Fuzzy Inference Systems
- **Benchmark suites:** CEC2017 (continuous), TSPLIB (combinatorial), UCI (classification), SAT (boolean)
- **Metrics:** Mean, std, best, convergence rate, and statistical significance
- **Reproducibility:** 230 passing tests, Docker isolation, CI/CD validation

This is the same empirical evaluation approach used in production ML model selection and comparison studies. See `benchmarks/` for the harness and `docs/quantum/` for research applications.

## License

Cyprus is [BSD Licensed](https://raw.github.com/gatesphere/cyprus/master/license/license.txt).


---

# Terminology

Cyprus uses several unique terms when it comes to programming languages.
These are described below.

- **Container** - an object that holds membranes, particles, and reaction definitons.

- **Environment** - a container that cannot be dissolved, nor whose walls can
be permeated.  A Cyprus program consists of at least one, possibly many,
environment definitions.

- **Membrane** - a container nested within an environment or another membrane.
Membranes can be dissolved and their walls can be permeated.

- **Particle** - a chemical, required for reactions to take place, and produced
by reactions.

- **Reaction** - a rule governing the interaction of particles within a membrane.

- **Priority** - an ordering of reactions.  Reactions with a higher priority
will be maximally applied before those with a lower priority.

---

# How Cyprus Works

Cyprus is governed by a single monolithic clock.  All activity within
all environments occurs in lockstep with the tick of the clock.  Each
tick, all reactions that are applicable within a given container are applied
maximally, obeying reaction priorities.

The clock stops ticking when no more
reaction applications can occur.  At this point, the particles contained by
the environments are interpreted as the final output of the program,
with everything else left in the system discarded as leftover state.

During the execution of a Cyprus program, membranes may dissolve, destroying
their reaction defenitions with them, but spilling their particles into
their parent container.  Environments cannot dissolve.

Particles may also osmose through their containing membrane's walls, either
targeting their container's parent, or a specific membrane by way of names.

Using named targets, a particle can osmose deeper into nested membranes,
or pass through multiple containing membranes.  Environments cannot be
osmosed through, though particles may osmose over environmental boundaries.

Reaction application is maximal, but non-deterministic: reactions are
applied in any valid order which obeys the assigned reaction priorities.

Cyprus is a Turing complete language, though using it for anything other
than fun and experimentation would be insane.  It is therefore an extremely
losely defined [Turing Tarpit](http://en.wikipedia.org/wiki/Turing_tarpit).

---

# Install and Usage

## Getting Cyprus

  1. Ensure you have Python3 ~~2.7 installed (not Python 3+!)~~
  2. Install funcparser lib with `pip install funcparserlib`
  3. Clone this repo


## Using Cyprus

```
Usage:

    $ python cyprus.py
    usage: python cyprus.py [-p | -V] <filename.cyp>
           python cyprus.py -v
           python cyprus.py -h
      -p: pretty-print(a parse tree and exit
      -V: display verbose output of the program's execution
      -v: display version info and exit
      -h: display this help text and exit
```

Convenience tools include:

Edit

```
    run.sh
```

or add to Makefile.

---

# Cyprus' grammar

Here's the grammar, in a modified EBNF:

    program        := {env}
    env            := "[", body, "]"
    membrane       := "(", body, ")"
    body           := <name>, {statement}
    statement      := membrane | expr
    expr           := exists | reaction | priority
    exists         := "exists", "~", name, {name}
    reaction       := "reaction", <"as", name>, "~", name, {name}, "::",
                       {symbol}
    priority       := "priority", "~", name, ">>", name
    name           := number | atom
    atom           := [A-Za-z], {[A-Za-z0-9]}
    number         := [0-9], {[0-9]} | {[0-9]}, ".", [0-9], {[0-9]}
    symbol         := atom | "!", name, <"!!", name> | "$", [name]


see [examples/README.md](examples/README.md)


Those examples, along with the grammar, show pretty much all you need to
know about writing Cyprus programs.

Planned features
----------------
  - Particle and membrane charges
  - Variable membrane permeability
  - Syntactic sugar for catalysts (`reaction~ *x :: x` == `reaction~ x :: x x`)
  - Clean up code (remove globals, comment, etc.)

WIP
---

python3 compatibility
