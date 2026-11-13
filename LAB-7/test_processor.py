from hypothesis import given, settings, strategies as st
from processor import sanitize_meter_id, parse_consumption_readings, format_billing_summary

SPECIAL_CHARS = ['!', '@', '#', '$', '%']


@settings(max_examples=500)
@given(st.text() | st.none())
def test_sanitize_meter_id_no_crash(s):
    try:
        result = sanitize_meter_id(s)
    except Exception as e:
        assert False, f"sanitize_meter_id crashed on {s!r} with: {type(e).__name__}: {e}"

    # Properties the output must satisfy
    assert isinstance(result, str), f"Expected str, got {type(result).__name__}"
    for ch in SPECIAL_CHARS:
        assert ch not in result, f"Special char {ch!r} left in output {result!r}"
    assert result == result.strip(), f"Output {result!r} has leading/trailing whitespace"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_parse_consumption_readings_safe(s):
    try:
        result = parse_consumption_readings(s)
    except Exception as e:
        assert False, f"parse_consumption_readings crashed on {s!r} with: {type(e).__name__}: {e}"

    # Properties the output must satisfy
    assert isinstance(result, list), f"Expected list, got {type(result).__name__}"
    for r in result:
        assert isinstance(r, int), f"Non-int value {r!r} in output"
        assert r >= 0, f"Negative consumption reading {r} accepted"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_format_billing_summary_safe(s):
    try:
        result = format_billing_summary(s)
    except Exception as e:
        assert False, f"format_billing_summary crashed on {s!r} with: {type(e).__name__}: {e}"

    assert isinstance(result, str), f"Expected str, got {type(result).__name__}"


# Extra: well-formed inputs must still produce the correct answer after hardening
@given(
    st.lists(st.integers(min_value=0, max_value=10**6), min_size=1, max_size=20)
)
def test_parse_consumption_readings_valid_roundtrip(nums):
    csv = ",".join(str(n) for n in nums)
    assert parse_consumption_readings(csv) == nums


@given(
    st.from_regex(r"[A-Za-z][A-Za-z ]{0,19}", fullmatch=True).map(str.strip).filter(bool),
    st.integers(min_value=0, max_value=10**6),
    st.from_regex(r"[A-Za-z][A-Za-z0-9 ]{0,9}", fullmatch=True).map(str.strip).filter(bool),
)
def test_format_billing_summary_valid(name, units, zone):
    result = format_billing_summary(f"{name}:{units}:{zone}")
    assert result == f"Customer {name} billed {units * 2} USD in {zone}"
