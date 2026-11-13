SPECIAL_CHARS = ['!', '@', '#', '$', '%']
MAX_INPUT_LENGTH = 10_000      # guard against oversized input (DoS)
MAX_READING_DIGITS = 12        # a single reading longer than this is not realistic


def sanitize_meter_id(meter_id):
    """Remove special characters and normalise a meter ID.

    Returns an empty string for None / non-string / oversized input
    instead of crashing.
    """
    if not isinstance(meter_id, str) or len(meter_id) > MAX_INPUT_LENGTH:
        return ""
    for ch in SPECIAL_CHARS:
        meter_id = meter_id.replace(ch, '')
    # strip AFTER removing special chars so "! A" doesn't leave a leading space
    return meter_id.strip().upper()


def _parse_reading(token):
    """Convert one CSV token into a non-negative int, or return None if invalid."""
    token = token.strip()
    # only plain ASCII digits: rejects '', '-5', '1.5', '1_0', unicode digits like '٣'
    if not token or not token.isascii() or not token.isdigit():
        return None
    if len(token) > MAX_READING_DIGITS:
        return None
    try:
        return int(token)
    except ValueError:
        return None


def parse_consumption_readings(readings_csv):
    """Parse a comma-separated list of meter readings.

    Invalid entries (empty, non-numeric, negative, too large) are skipped.
    Returns [] for None / non-string / oversized input.
    """
    if not isinstance(readings_csv, str) or len(readings_csv) > MAX_INPUT_LENGTH:
        return []
    readings = []
    for token in readings_csv.split(','):
        value = _parse_reading(token)
        if value is not None:
            readings.append(value)
    return readings


def format_billing_summary(account_record):
    """Build a billing summary from a 'Name:Usage:Zone' record.

    Returns an 'Invalid account record' message instead of crashing on
    malformed input.
    """
    if not isinstance(account_record, str) or len(account_record) > MAX_INPUT_LENGTH:
        return "Invalid account record: expected a string in the format Name:Usage:Zone"

    parts = account_record.split(':')
    if len(parts) != 3:
        return "Invalid account record: expected exactly 3 fields (Name:Usage:Zone)"

    customer_name = parts[0].strip()
    zone = parts[2].strip()
    if not customer_name:
        return "Invalid account record: customer name is empty"
    if not zone:
        return "Invalid account record: zone is empty"

    units = _parse_reading(parts[1])
    if units is None:
        return "Invalid account record: usage must be a non-negative whole number"

    return f"Customer {customer_name} billed {units * 2} USD in {zone}"


def safe_input(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def main():
    print("==== Running sanitize_meter_id ====")
    raw_id = safe_input("Enter a meter ID with prefixes (!,@,#,$,%): ")
    clean_id = sanitize_meter_id(raw_id)
    print("Sanitized Meter ID:", clean_id if clean_id else "(invalid / empty meter ID)")

    print("\n==== Running parse_consumption_readings ====")
    csv_input = safe_input("Enter consumption readings (e.g. 10,25,30): ")
    readings_list = parse_consumption_readings(csv_input)
    print("Parsed Readings:", readings_list)

    print("\n==== Running format_billing_summary ====")
    summary_input = safe_input("Enter account record (Name:Usage:Zone): ")
    summary = format_billing_summary(summary_input)
    print("Billing Summary:", summary)


if __name__ == "__main__":
    main()