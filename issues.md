# Issues Found and Fixed — `library_system.py`

**Student:** Nyssa Bansal (PES1UG24CS306) · **Repo:** L5_01_library_fines

Line numbers refer to the **original** file. Ordered by severity (high/medium first).

| # | Issue | Tool / Code | Type | Severity | Line(s) | Description | Fix Approach |
|---|-------|-------------|------|----------|---------|-------------|--------------|
| 1 | Use of `eval` | Bandit B307, Pylint W0123 | Security | High (Bandit: Medium, High confidence) | 45 | `fine_from_rule` runs `eval()` on a rule string, so any Python code passed in as a "rule" (e.g. `__import__('os').system(...)`) would execute. | Replaced with a small AST evaluator (`ast.parse` + whitelist of `+ - * / //`, unary minus, numeric constants and the name `days`). Anything else raises `ValueError`. |
| 2 | Mutable default argument | Pylint W0102 | Bug | High | 9, 12, 14 | `dates=[]` is created once and shared by every call, so "loan dates on record" kept climbing (1, 2, 3...) across different students. | Default changed to `None`; a fresh list is created inside the function. |
| 3 | Global fine rate mutated on renewal | Pylint W0603 (global-statement) | Bug | High | 27–31 | `renewBook` did `global FINE_PER_DAY` and incremented it, so one long renewal permanently raised the fine for **everyone** (5 days showed 15 instead of 10). | `renew_book` now computes a per-loan rate (`FINE_PER_DAY + surcharge` for renewals > 14 days) and returns it; the constant is never reassigned. Magic numbers moved to `LONG_RENEWAL_DAYS` / `LONG_RENEWAL_SURCHARGE`. |
| 4 | Bare `except: pass` | Bandit B110, Pylint W0702, Flake8 E722 | Bug / Security | Medium | 21–22 | Swallowed every exception (even `KeyboardInterrupt`) silently, so returning a book that was never borrowed gave no feedback. | Catch only `KeyError`/`ValueError` and print a "No active loan" message. |
| 5 | Files opened without `with` / encoding | Pylint R1732, W1514 | Bug | Medium | 34, 40 | Files closed manually, so an exception between `open` and `close` leaks the handle; encoding depends on the platform. Missing/corrupt `loans.json` crashed the program. | Use `with open(..., encoding="utf-8")` plus `json.load`/`json.dump`; `load_records` handles `FileNotFoundError`/`JSONDecodeError`. |
| 6 | `global loans` reassignment | Pylint W0603 | Code quality | Medium | 35–36 | `load_records` rebinds the module global. | Mutate in place with `loans.clear()` + `loans.update(data)`; no `global` needed. |
| 7 | Unvalidated user input | Not flagged (found by running) | Bug | Medium | 62–63 | `int(days)` crashed with `ValueError` on input like `abc`; negative input produced a negative fine. | New `read_days()` helper validates input and falls back to 0 with a message. |
| 8 | Negative fines | Not flagged (found by running) | Bug | Medium | 24–25, 60 | `calculate_fine(-3)` returned `-9`. | `max(0, days_overdue) * rate`. |
| 9 | Non-string book id accepted | Not flagged (found by running) | Bug | Low | 56 | `4521` (int) was stored as a book id; empty student id was ignored silently. | Type check in `add_book_loan`; both rejections now print a message. |
| 10 | Unused import `os` | Pylint W0611, Flake8 F401 | Code quality | Low | 2 | Imported but never used. | Removed. |
| 11 | Non-snake_case name | Pylint C0103 | Style | Low | 27, 58 | `renewBook` breaks PEP 8 naming. | Renamed to `renew_book`. |
| 12 | Missing docstrings | Pylint C0114, C0116 | Style | Low | 1, 9–52 | No module or function docstrings. | Added module and function docstrings. |
| 13 | Old `%` / `+` string formatting | Pylint C0209 | Style | Low | 14, 31 | Harder to read; `+` concatenation would crash on non-str ids. | Converted to f-strings. |
| 14 | Iterating dict keys then indexing | Not flagged (cleanup) | Style | Low | 49–50 | `for s in loans: loans[s]`. | `for student, books in loans.items()`. |
| 15 | Missing blank lines | Flake8 E302, E305 | Style | Low | 9–52, 68 | Top-level defs need 2 blank lines. | Added 2 blank lines between top-level definitions. |
| 16 | Lines too long | Flake8 E501 | Style | Low | 14, 31 | Lines over 79 chars. | Split f-strings / expressions across lines. |
| 17 | `main()` runs on import | Flake8 E305 (context), best practice | Code quality | Low | 68 | Importing the module would run the demo and prompt for input. | Wrapped in `if __name__ == "__main__":`. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.07/10 (22 messages) | **10.00/10** |
| Bandit | 2 issues (1 Medium, 1 Low) | **0 issues** |
| Flake8 | 14 issues | **0 issues** |

Reports are in `reports/before/` and `reports/after/`.
