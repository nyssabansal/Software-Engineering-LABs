# Reflection — Lab 5: Static Code Analysis

**Student:** Nyssa Bansal (PES1UG24CS306) · **Repo:** L5_01_library_fines

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style issues and the simple Pylint ones: blank lines, long lines, the unused `os` import, renaming `renewBook` to `renew_book`, adding docstrings and switching to f-strings. They are mechanical and don't change behaviour.

The hardest was replacing `eval()` in `fine_from_rule`. Bandit suggests `ast.literal_eval`, but that only parses literals, so it can't handle a rule like `days * 2 + 10`. I had to write a small evaluator that walks the AST and only allows arithmetic operators, numbers and the name `days`. The global `FINE_PER_DAY` change was also tricky, because Pylint only reports "using the global statement" as a style warning. The real issue was a logic bug: one long renewal raised the fine rate for everyone, which I only understood after running the program and seeing a 5-day fine come out as 15 instead of 10.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Nothing was a real false positive, but some reports overstated or understated how serious an issue was:
- Bandit B110 (try/except/pass) is rated **Low** and isn't a security hole on its own here. It mattered more as a correctness problem: silently ignoring a bad book return.
- Bandit rated `eval` as **Medium**, while in practice it is the most dangerous line in the file (arbitrary code execution if the rule ever came from user input).
- Pylint's `global-statement` for `load_records` is a design warning more than a bug. The code worked, it just wasn't clean.

There were also **false negatives**: the tools missed negative fines, the crash on non-numeric input, and the integer book id. I only found those by running the program and testing inputs like `abc` and `-4`.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run the three tools through a `pre-commit` hook (and in the editor via the VS Code Pylint/Flake8 extensions) so issues are caught before a commit is made.
- **CI:** add a GitHub Actions step that runs `flake8`, `pylint --fail-under=9.5` and `bandit -r . -ll` on every push and pull request, and blocks the merge if any of them fail.
- **Configuration:** keep a shared `.pylintrc` / `setup.cfg` so the whole team uses the same rules, and use `# nosec` / `# pylint: disable` only with a comment explaining why.
- Static analysis complements unit tests rather than replacing them, since several bugs here were logic errors no linter flagged.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Security:** no more `eval`, so a fine rule can no longer run arbitrary code.
- **Correctness:** loan-date counts no longer leak between calls, renewals no longer change everyone's fine rate, fines can't be negative, and bad input no longer crashes the program.
- **Robustness:** files are always closed (`with`), use an explicit encoding, and a missing or corrupt `loans.json` is handled. Failed operations print a message instead of failing silently. The demo only runs under `if __name__ == "__main__"`, so the module can be imported safely.
- **Readability:** docstrings, snake_case names, f-strings, named constants instead of magic numbers, and PEP 8 formatting.
- **Measured:** Pylint went from 6.07 to 10.00/10, Bandit from 2 issues to 0, Flake8 from 14 to 0.
