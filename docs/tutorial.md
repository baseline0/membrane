

# tick by tick

```
Clock tick: 0
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: []
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
            (name: 3
             symbols: [a, c]
             rules: [[a] -> [a, b] (1), [a] -> [b, $] (1), [c] -> [c, c] (1)]
             staging area: []
             Membranes:
            )
        )
    )
]
Clock tick: 1
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: []
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
            (name: 3
             symbols: [a, b, c, c]
             rules: [[a] -> [a, b] (1), [a] -> [b, $] (1), [c] -> [c, c] (1)]
             staging area: []
             Membranes:
            )
        )
    )
]
Clock tick: 2
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: []
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
            (name: 3
             symbols: [b, c, c, c, c, a, b]
             rules: [[a] -> [a, b] (1), [a] -> [b, $] (1), [c] -> [c, c] (1)]
             staging area: []
             Membranes:
            )
        )
    )
]
Clock tick: 3
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: [b, b, b, c, c, c, c, c, c, c, c]
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
        )
    )
]
Clock tick: 4
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: [c, c, c, c, d, d, d]
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
        )
    )
]
Clock tick: 5
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: [c, c, d, e, d, e, d, e]
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
        )
    )
]
Clock tick: 6
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: []
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
        (name: 2
         symbols: [e, e, e, c, d, e, d, e, d, e]
         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
         staging area: []
         Membranes:
        )
    )
]
Clock tick: 7
[name: env
 symbols: []
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: [e, e, e, e, e, e, d, e, d, e, d, e]
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
    )
]
Clock tick: 8
[name: env
 symbols: [e, e, e, e, e, e, e, e, e]
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: [d, d, d]
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
    )
]
Clock tick: 9
[name: env
 symbols: [e, e, e, e, e, e, e, e, e]
 rules: []
 staging area: []
 Membranes:
    (name: 1
     symbols: [d, d, d]
     rules: [[e] -> [!e] (1)]
     staging area: []
     Membranes:
    )
]
env: [e, e, e, e, e, e, e, e, e]
```
---

as it looks w current logging

INFO:root:Clock tick: 0
INFO:root: [name: env
INFO:root: symbols: []
INFO:root: rules: []
INFO:root: staging area: []
INFO:root: Membranes:
INFO:root:     (name: 1
INFO:root:     symbols: []
INFO:root:     rules: [[e] -> [!e] (1)]
INFO:root:     staging area: []
INFO:root:     Membranes:
INFO:root:         (name: 2
INFO:root:         symbols: []
INFO:root:         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
INFO:root:         staging area: []
INFO:root:         Membranes:
INFO:root:             (name: 3
INFO:root:             symbols: [a, c]
INFO:root:             rules: [[a] -> [a, b] (1), [a] -> [b, $] (1), [c] -> [c, c] (1)]
INFO:root:             staging area: []
INFO:root:             Membranes:
INFO:root:
INFO:root:
INFO:root:
INFO:root:]
INFO:root:Clock tick: 1
INFO:root: [name: env
INFO:root: symbols: []
INFO:root: rules: []
INFO:root: staging area: []
INFO:root: Membranes:
INFO:root:     (name: 1
INFO:root:     symbols: []
INFO:root:     rules: [[e] -> [!e] (1)]
INFO:root:     staging area: []
INFO:root:     Membranes:
INFO:root:         (name: 2
INFO:root:         symbols: [c, c, b]
INFO:root:         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
INFO:root:         staging area: []
INFO:root:         Membranes:
INFO:root:
INFO:root:
INFO:root:]
INFO:root:Clock tick: 2
INFO:root: [name: env
INFO:root: symbols: []
INFO:root: rules: []
INFO:root: staging area: []
INFO:root: Membranes:
INFO:root:     (name: 1
INFO:root:     symbols: []
INFO:root:     rules: [[e] -> [!e] (1)]
INFO:root:     staging area: []
INFO:root:     Membranes:
INFO:root:         (name: 2
INFO:root:         symbols: [c, d]
INFO:root:         rules: [[b] -> [d] (1), [d] -> [d, e] (1), [c, c] -> [c] (2)[c1]), [c] -> [$] (1)[c2])]
INFO:root:         staging area: []
INFO:root:         Membranes:
INFO:root:
INFO:root:
INFO:root:]
INFO:root:Clock tick: 3
INFO:root: [name: env
INFO:root: symbols: []
INFO:root: rules: []
INFO:root: staging area: []
INFO:root: Membranes:
INFO:root:     (name: 1
INFO:root:     symbols: [d, e]
INFO:root:     rules: [[e] -> [!e] (1)]
INFO:root:     staging area: []
INFO:root:     Membranes:
INFO:root:
INFO:root:]
INFO:root:Clock tick: 4
INFO:root: [name: env
INFO:root: symbols: [e]
INFO:root: rules: []
INFO:root: staging area: []
INFO:root: Membranes:
INFO:root:     (name: 1
INFO:root:     symbols: [d]
INFO:root:     rules: [[e] -> [!e] (1)]
INFO:root:     staging area: []
INFO:root:     Membranes:
INFO:root:
INFO:root:]
INFO:root:Clock tick: 5
INFO:root: [name: env
INFO:root: symbols: [e]
INFO:root: rules: []
INFO:root: staging area: []
INFO:root: Membranes:
INFO:root:     (name: 1
INFO:root:     symbols: [d]
INFO:root:     rules: [[e] -> [!e] (1)]
INFO:root:     staging area: []
INFO:root:     Membranes:
INFO:root:
INFO:root:]
INFO:root:env: [e]
