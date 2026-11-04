"""
Lab 6 - Code (line) coverage tests for water_utility_billing.py
SRN: PES1UG24CS306

Goal: make every statement in the module execute at least once.

Run:
    coverage run -m pytest CodeCoverageTest_PES1UG24CS306_water_utility_billing.py
    coverage report -m
"""
import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


def make_account(usage_blocks, active=True, commercial=False, leak_waiver=False):
    return {
        "is_active": active,
        "is_commercial": commercial,
        "has_leak_waiver": leak_waiver,
        "usage_blocks": usage_blocks,
    }


# ---------------- calculate_water_bill ----------------

def test_single_active_residential():
    # starter test: 10 + 30*1.5 = 55
    result = calculate_water_bill([make_account([30])], 10.0)
    assert result["total_billed"] == 55.0
    assert result["status"] == "NORMAL"


def test_invalid_accounts_type_raises():
    # line 3: accounts is not a list
    with pytest.raises(ValueError):
        calculate_water_bill("not a list", 10.0)


def test_negative_base_fee_raises():
    # line 3: base_fee < 0
    with pytest.raises(ValueError):
        calculate_water_bill([], -1.0)


def test_inactive_account_is_skipped():
    # line 10: inactive account -> continue
    accounts = [make_account([500], active=False), make_account([30])]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 55.0


def test_residential_mixed_usage_blocks():
    # 0 -> flagged + skipped (lines 18-19)
    # 60 -> 60*2.5 = 150 (line 28)
    # 30 -> 30*1.5 = 45 (line 30)
    # 120 -> flagged, residential 120*4.5 = 540, then break (lines 22-25)
    # 40 -> never reached because of break
    result = calculate_water_bill([make_account([0, 60, 30, 120, 40])], 10.0)
    assert result["total_billed"] == 10 + 150 + 45 + 540
    assert result["status"] == "NORMAL"


def test_commercial_high_usage():
    # line 26: commercial over 100 -> 120*3.5 = 420
    result = calculate_water_bill([make_account([120], commercial=True)], 10.0)
    assert result["total_billed"] == 430.0


def test_leak_waiver_applied_over_200():
    # 10 + 100*2.5 = 260 > 200 -> minus 50 (line 34)
    result = calculate_water_bill([make_account([100], leak_waiver=True)], 10.0)
    assert result["total_billed"] == 210.0


def test_excessive_flags_status():
    # six invalid blocks -> flagged_accounts = 6 > 5 (line 40)
    result = calculate_water_bill([make_account([0, -5, 0, -1, 0, -2])], 10.0)
    assert result["total_billed"] == 10.0
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_no_activity_status():
    # nothing billed (line 42)
    result = calculate_water_bill([], 0.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


# ---------------- check_meter_tampering ----------------

def test_tampering_no_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_tampering_suspected():
    # two consecutive negative deltas
    assert check_meter_tampering([[5, -1, -2]]) == "TAMPER_SUSPECTED"


def test_tampering_clear():
    assert check_meter_tampering([[1, 2, 3]]) == "CLEAR"
