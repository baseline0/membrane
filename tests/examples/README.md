# Example programs

Here's an annotated example program, (example1.cyp) that generates
perfect squares:

```
// generate perfect squares
// comments are defined with // to the end of the line
[env       // open an environment, call it "env"
    (1       // open a membrane, call it "1"
    (2     // open a membrane, call it "2"
        (3   // open a membrane, call it "3"
        // seed the membrane "3" with 2 particles, "a" and "c"
        exists~   a c

        // define some reactions (in "3")
        reaction~   a :: a b  // take an "a", produce "a" and "b"
        reaction~   a :: b $  // take an "a", produce "b" and dissolve self
                                // reaction~ a :: b $3 would do the same in
                                //                     this situation.
                                // reaction~ a :: b $foo would dissolve
                                //                       container "foo"
        reaction~   c :: c c  // take a "c", produce two "c"s
        )

        // define some reactions (in "2")
        reaction~         b :: d
        reaction~         d :: d e
        reaction as c1~ c c :: c  // name this reaction c1
        reaction as c2~   c :: $  // name this reaction c2

        // define rule priority
        priority~        c1 >> c2 // c1 must be maximally applied before c2
        // named reactions are required for rule priorities
    )

    // define a reaction (in "3")
    reaction~ e :: !e // take an "e", osmose an "e" to parent container
                        // reaction~ e :: !e!!env would do the same in this
                        //                        situation.
                        // reaction~ e :: !e!!foo would make "e" osmose to
                        //                        container "foo"
    )
]
```

The output here is the amount of "e" particles in the environment at the
end of the program's execution.

Here's another example annotated program (test/hello.cyp), that produces
a "hello, world!" effect:

```
// hello world in cyprus

[ // names are optional
    (
    exists~ hello
    reaction~ hello :: hello world $
    )
]
```


---

# example 1

run with:

```
make example1
```

**output**

```
{Program}
`-- {Environment}
    |-- Token('name', 'env')
    `-- {Statement}
        `-- {Membrane}
            |-- Token('number', '1')
            |-- {Statement}
            |   `-- {Membrane}
            |       |-- Token('number', '2')
            |       |-- {Statement}
            |       |   `-- {Membrane}
            |       |       |-- Token('number', '3')
            |       |       |-- {Statement}
            |       |       |   |-- Token('kw_exists', 'exists')
            |       |       |   |-- Token('op_tilde', '~')
            |       |       |   |-- Token('name', 'a')
            |       |       |   `-- Token('name', 'c')
            |       |       |-- {Statement}
            |       |       |   |-- Token('kw_reaction', 'reaction')
            |       |       |   |-- None
            |       |       |   |-- Token('op_tilde', '~')
            |       |       |   |-- Token('name', 'a')
            |       |       |   |-- Token('op_production', '::')
            |       |       |   |-- Token('name', 'a')
            |       |       |   `-- Token('name', 'b')
            |       |       |-- {Statement}
            |       |       |   |-- Token('kw_reaction', 'reaction')
            |       |       |   |-- None
            |       |       |   |-- Token('op_tilde', '~')
            |       |       |   |-- Token('name', 'a')
            |       |       |   |-- Token('op_production', '::')
            |       |       |   |-- Token('name', 'b')
            |       |       |   |-- Token('op_dissolve', '$')
            |       |       |   `-- None
            |       |       `-- {Statement}
            |       |           |-- Token('kw_reaction', 'reaction')
            |       |           |-- None
            |       |           |-- Token('op_tilde', '~')
            |       |           |-- Token('name', 'c')
            |       |           |-- Token('op_production', '::')
            |       |           |-- Token('name', 'c')
            |       |           `-- Token('name', 'c')
            |       |-- {Statement}
            |       |   |-- Token('kw_reaction', 'reaction')
            |       |   |-- None
            |       |   |-- Token('op_tilde', '~')
            |       |   |-- Token('name', 'b')
            |       |   |-- Token('op_production', '::')
            |       |   `-- Token('name', 'd')
            |       |-- {Statement}
            |       |   |-- Token('kw_reaction', 'reaction')
            |       |   |-- None
            |       |   |-- Token('op_tilde', '~')
            |       |   |-- Token('name', 'd')
            |       |   |-- Token('op_production', '::')
            |       |   |-- Token('name', 'd')
            |       |   `-- Token('name', 'e')
            |       |-- {Statement}
            |       |   |-- Token('kw_reaction', 'reaction')
            |       |   |-- Token('kw_as', 'as')
            |       |   |-- Token('name', 'c1')
            |       |   |-- Token('op_tilde', '~')
            |       |   |-- Token('name', 'c')
            |       |   |-- Token('name', 'c')
            |       |   |-- Token('op_production', '::')
            |       |   `-- Token('name', 'c')
            |       |-- {Statement}
            |       |   |-- Token('kw_reaction', 'reaction')
            |       |   |-- Token('kw_as', 'as')
            |       |   |-- Token('name', 'c2')
            |       |   |-- Token('op_tilde', '~')
            |       |   |-- Token('name', 'c')
            |       |   |-- Token('op_production', '::')
            |       |   |-- Token('op_dissolve', '$')
            |       |   `-- None
            |       `-- {Statement}
            |           |-- Token('kw_priority', 'priority')
            |           |-- Token('op_tilde', '~')
            |           |-- Token('name', 'c1')
            |           |-- Token('op_priority_maximal', '>>')
            |           `-- Token('name', 'c2')
            `-- {Statement}
                |-- Token('kw_reaction', 'reaction')
                |-- None
                |-- Token('op_tilde', '~')
                |-- Token('name', 'e')
                |-- Token('op_production', '::')
                |-- Token('op_osmose', '!')
                |-- Token('name', 'e')
                `-- None
```
