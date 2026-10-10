# Formula Troubleshooting: Symbol Aliasing and Assumptions

Covers the formula pipeline in `paper/`: formulas are defined in `paper/model.py`, validated by `paper/validate_formulas.py`, and consumed by `paper/build_slides.py` and `paper/build_paper.py`.

Run commands from the repo root with `just formula-check` (it runs `validate_formulas.py` inside `paper/`). `validate_formulas.py` loads `model.py` by relative path, so running it from any other directory fails.

Scope note: no test under `tests/` covers aliasing or assumptions. `paper/stress_test_formulas.py` is a script, not a pytest module, and `pyproject.toml` sets `testpaths` to `tests/unit`, `tests/integration`, `tests/e2e`.

## How rendering works

`Formula.to_latex()` in `paper/model.py` runs three steps:

1. **Assumptions:** for each key in `Formula.assumptions`, `expr.subs(Symbol(name), Symbol(name, **assumptions))`.
2. **Render:** `sp.latex(expr, **rendering_opts)`. Defaults are `mode="plain"`, `fold_short_frac=False`, `mul_symbol="cdot"`.
3. **Alias:** for each `code_name -> display_latex` in `Formula.symbols`, `latex_str.replace(code_name, display_latex)`.

`Formula.to_dict()` exports the same LaTeX into `qips_equations.json`, which the builders read.

## Symptom: `Formula 'X' not found`

- **Where:** `validate_formulas()` in `paper/validate_formulas.py`.
- **Cause:** a `{{formula:X}}` reference in `presentation.md` has no matching `id` in `model.FORMULAS`.
- **Fix:** correct the spelling against the `Available:` list in the error, or add the formula to `FORMULAS`.

## Symptom: `Symbols without assumptions: ...`

- **Where:** `validate_symbol_assumptions()` in `paper/validate_formulas.py`.
- **What it checks:** the names in `formula.expr.free_symbols` must be keys of `formula.assumptions`. It does not check the values, so `{"q": {"positive": True}}` passes for any `q`.
- **Modes:** without `--strict` this is a warning. With `--strict`, `main()` returns failure before reference validation runs.
- **Fix:** add an entry for each free symbol to the formula's `assumptions` dict.

## Symptom: assumptions do not change the rendered LaTeX

- **Why:** the module-level symbols `n`, `m`, `k`, `r`, `d`, `t` in `model.py` already carry `integer=True, positive=True`. Substituting `Symbol(name)` with `Symbol(name, **assumptions)` therefore changes nothing for those symbols.
- **Observed:** `Formula(expr=n*2, assumptions={"n": {...}})` renders as `2cdotn`. The LaTeX output contains no assumption information (see `2^{d}`, `2cdotn` in `paper/qips_equations.json`).
- **Implication:** `assumptions` is a record of intent, exported to `to_dict()` and `formula_index.md`. It does not alter the rendered output for the current formulas.

## Symptom: alias produces broken LaTeX

- **Why:** the alias step in `to_latex()` is a plain `str.replace` with no word boundaries or LaTeX awareness.
- **Observed:**
  - `symbols={"n": r"\theta"}` on `sin(n)` yields `\si\theta{\left(\theta \right)}`. The `n` inside `\sin` is replaced.
  - On `n*theta_x` the output is `\thetacdot\theta_{x}`. The missing space makes `\thetacdot` an undefined control sequence.
- **Current status:** no entry in `FORMULAS` sets `symbols` (checked), so this path is not exercised by the current build.
- **Advice:** if you add an alias, inspect the rendered LaTeX by hand. Do not rely on the validator, which does not look at `symbols`.

## Symptom: multiplication renders as `2cdotn`

- **Where:** `rendering_opts={"mul_symbol": "cdot"}` in `Formula` (`model.py`) and in `mult_rule1` and `objects_per_step`.
- **Observed:** `paper/qips_equations.json` contains `"2cdotn"` and `"\\left( n \\mapsto 2cdotn \\right)"`. The backslash is missing.
- **Downstream effect:** `generate_formulas()` in `paper/build_paper.py` does `replace(r"\cdot", "dot")`. That pattern never matches because the JSON has no backslash.
- **Not verified:** the exact `mul_symbol` value that sympy expects. Check sympy's `latex` options before changing it, then re-run `just formula-check`.

## Symptom: `|param=value` in slides has no effect

- **Where:** `substitute_formulas()` in `paper/build_slides.py`.
- **Observed in code:** the docstring says `{{formula:mult_rule1|n=3}}` produces `2 \cdot 3 = 6`. The function only appends `[params: ...]` as text after the unsubstituted formula, with a `# For now` comment.
- **Implication:** parameter substitution is not implemented. Do not rely on `|params` for values.

## Symptom: `<!-- formula not found: X -->` in generated slides

- **Where:** `substitute_formulas()` in `paper/build_slides.py`.
- **Cause:** the id is missing from `qips_equations.json`, which is regenerated from `model.py` by `generate_formulas_json()`. The `validate_formulas.py` check is the place that catches this before the build.

## Symptom: `model.py did not generate qips_equations.json`

- **Where:** `generate_formulas()` in `paper/build_paper.py`.
- **Behaviour:** prints a warning and returns success, so the paper build continues without formulas.

## Side effects

- `validate_formulas.py` writes `formula_index.md` to the current directory on every successful run (`generate_formula_index()`). The file is not tracked by git, so it appears as untracked output.

## Not verified

- How the LaTeX renders in Typst (`paper/build_paper.py`) or Marp slides. Only the strings were checked, not built output.
- The `|params` behaviour in the paper build path. Only `build_slides.py` was read.
