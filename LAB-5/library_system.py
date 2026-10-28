"""Library fine and book renewal system.

Tracks which student has borrowed which book, calculates overdue fines,
handles renewals and saves loan records to a JSON file.
"""
import ast
import json
import operator
from datetime import datetime

# Global state
loans = {}
FINE_PER_DAY = 2
LONG_RENEWAL_DAYS = 14
LONG_RENEWAL_SURCHARGE = 1


def add_book_loan(student_id, book_id, dates=None):
    """Record that student_id has borrowed book_id."""
    if dates is None:
        dates = []
    if not student_id:
        print("Loan rejected: student id is empty")
        return
    if not isinstance(book_id, str):
        print(f"Loan rejected: book id {book_id!r} must be a string")
        return
    dates.append(str(datetime.now()))
    loans[student_id] = loans.get(student_id, []) + [book_id]
    print(f"{student_id} borrowed {book_id} "
          f"(loan dates on record: {len(dates)})")


def return_book(student_id, book_id):
    """Remove book_id from student_id's loans, if it is on loan."""
    try:
        loans[student_id].remove(book_id)
        if len(loans[student_id]) == 0:
            del loans[student_id]
    except (KeyError, ValueError):
        print(f"No active loan of {book_id} for {student_id}")


def calculate_fine(days_overdue, rate=FINE_PER_DAY):
    """Return the fine for days_overdue days; never negative."""
    return max(0, days_overdue) * rate


def renew_book(student_id, book_id, extra_days):
    """Renew a loan and return the daily fine rate that applies to it.

    Long renewals carry a surcharge for that loan only; the shared
    FINE_PER_DAY constant is no longer modified.
    """
    rate = FINE_PER_DAY
    if extra_days > LONG_RENEWAL_DAYS:
        rate += LONG_RENEWAL_SURCHARGE
    print(f"Renewed {book_id} for {student_id} by {extra_days} days "
          f"(fine rate {rate}/day)")
    return rate


def load_records(file="loans.json"):
    """Replace the in-memory loans with the records stored in file."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as err:
        print(f"Could not load records from {file}: {err}")
        return
    loans.clear()
    loans.update(data)


def save_records(file="loans.json"):
    """Write the in-memory loans to file as JSON."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(loans, f)


_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
}


def _eval_node(node, days):
    """Evaluate a whitelisted arithmetic AST node."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, days)
    if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id == "days":
        return days
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        left = _eval_node(node.left, days)
        right = _eval_node(node.right, days)
        return _ALLOWED_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.operand, days))
    raise ValueError("Unsupported expression in fine rule")


def fine_from_rule(rule, days):
    """Compute a fine from an arithmetic rule such as 'days * 2 + 10'."""
    return _eval_node(ast.parse(rule, mode="eval"), days)


def print_report():
    """Print every student and the books they currently have on loan."""
    print("Loan Report")
    for student, books in loans.items():
        print(student, "->", books)


def read_days(prompt):
    """Ask for a non-negative whole number of days; default 0."""
    raw = input(prompt).strip() or "0"
    try:
        days = int(raw)
    except ValueError:
        print(f"'{raw}' is not a whole number, using 0")
        return 0
    if days < 0:
        print("Days cannot be negative, using 0")
        return 0
    return days


def main():
    """Run a short demonstration of the library system."""
    add_book_loan("S101", "B-ALGO")
    add_book_loan("S102", "B-NETW")
    add_book_loan("", "B-DBMS")
    add_book_loan("S103", 4521)  # rejected: book id must be a string
    return_book("S999", "B-NONE")
    renew_book("S101", "B-ALGO", 21)
    print("Fine for 5 days:", calculate_fine(5))
    print("Fine for -3 days:", calculate_fine(-3))
    print("Fine via rule:", fine_from_rule("days * 2 + 10", 4))
    days = read_days("Days overdue for S102 (press Enter for 0): ")
    print("S102 owes:", calculate_fine(days))
    save_records()
    load_records()
    print_report()


if __name__ == "__main__":
    main()
