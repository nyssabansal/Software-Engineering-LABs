"""
Lab 6 - Branch coverage tests for water_utility_billing.py
SRN: PES1UG24CS306

Goal: every decision (if / elif / for) evaluates to both True and False.
Each test notes which branch(es) it targets.

Run:
    coverage run --branch -m pytest BranchCoverageTest_PES1UG24CS306_water_utility_billing.py
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


# ============ calculate_water_bill ============

# --- input validation: `if not isinstance(...) or base_fee < 0` ---

@pytest.mark.parametrize("accounts, base_fee", [
    ("not a list", 10.0),   # isinstance check True
    (None, 10.0),
    ({"is_active": True}, 10.0),
    ([], -0.01),            # base_fee < 0 True
])
def test_invalid_input_raises(accounts, base_fee):
    with pytest.raises(ValueError):
        calculate_water_bill(accounts, base_fee)


def test_valid_input_zero_base_fee_allowed():
    # validation False branch with the boundary base_fee == 0
    result = calculate_water_bill([make_account([10])], 0.0)
    assert result["total_billed"] == 15.0


# --- outer loop: `for account in accounts` ---

def test_empty_accounts_loop_not_entered():
    # loop body never runs; total stays 0 -> NO_ACTIVITY
    result = calculate_water_bill([], 5.0)
    assert result == {"total_billed": 0.0, "status": "NO_ACTIVITY"}


# --- `if not account.get("is_active", False)` ---

def test_inactive_account_skipped():
    accounts = [make_account([500], active=False), make_account([30])]
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 55.0


def test_missing_is_active_defaults_to_inactive():
    # default False -> treated as inactive
    result = calculate_water_bill([{"usage_blocks": [30]}], 10.0)
    assert result == {"total_billed": 0.0, "status": "NO_ACTIVITY"}


def test_all_inactive_gives_no_activity():
    accounts = [make_account([30], active=False), make_account([80], active=False)]
    assert calculate_water_bill(accounts, 10.0)["status"] == "NO_ACTIVITY"


# --- inner loop: `for usage in usage_blocks` ---

def test_active_account_with_no_usage_blocks():
    # inner loop not entered -> only base fee
    result = calculate_water_bill([make_account([])], 10.0)
    assert result == {"total_billed": 10.0, "status": "NORMAL"}


def test_missing_usage_blocks_key_defaults_to_empty():
    result = calculate_water_bill([{"is_active": True}], 10.0)
    assert result["total_billed"] == 10.0


# --- `if usage <= 0` ---

@pytest.mark.parametrize("bad_usage", [0, -1, -50.5])
def test_non_positive_usage_flagged_and_skipped(bad_usage):
    result = calculate_water_bill([make_account([bad_usage, 10])], 10.0)
    # bad block adds nothing, 10*1.5 = 15
    assert result["total_billed"] == 25.0


# --- tier decisions: `if usage > 100` / `elif usage > 50` / else ---

@pytest.mark.parametrize("usage, expected", [
    (1, 10 + 1 * 1.5),        # lowest valid value
    (50, 10 + 50 * 1.5),      # boundary: not > 50 -> 1.5 rate
    (51, 10 + 51 * 2.5),      # just above 50 -> 2.5 rate
    (100, 10 + 100 * 2.5),    # boundary: not > 100 -> 2.5 rate
    (101, 10 + 101 * 4.5),    # just above 100, residential -> 4.5 rate
])
def test_residential_tier_boundaries(usage, expected):
    result = calculate_water_bill([make_account([usage])], 10.0)
    assert result["total_billed"] == round(expected, 2)


def test_commercial_over_100_rate():
    # `if not is_commercial` False -> 3.5 rate
    result = calculate_water_bill([make_account([101], commercial=True)], 10.0)
    assert result["total_billed"] == round(10 + 101 * 3.5, 2)


def test_commercial_below_100_uses_normal_tiers():
    result = calculate_water_bill([make_account([40, 70], commercial=True)], 10.0)
    assert result["total_billed"] == 10 + 40 * 1.5 + 70 * 2.5


def test_residential_over_100_breaks_out_of_loop():
    # `if not is_commercial` True -> break, so the 30 after it is NOT billed
    result = calculate_water_bill([make_account([120, 30])], 10.0)
    assert result["total_billed"] == 10 + 120 * 4.5


def test_commercial_over_100_continues_loop():
    # commercial does not break, so the 30 after it IS billed
    result = calculate_water_bill([make_account([120, 30], commercial=True)], 10.0)
    assert result["total_billed"] == 10 + 120 * 3.5 + 30 * 1.5


def test_break_only_affects_current_account():
    accounts = [make_account([150, 40]), make_account([20])]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == (10 + 150 * 4.5) + (10 + 20 * 1.5)


# --- leak waiver: `if has_leak_waiver` and `if acct_total > 200.0` ---

def test_no_leak_waiver_no_deduction():
    result = calculate_water_bill([make_account([100])], 10.0)
    assert result["total_billed"] == 260.0


def test_leak_waiver_applied_over_200():
    result = calculate_water_bill([make_account([100], leak_waiver=True)], 10.0)
    assert result["total_billed"] == 210.0


def test_leak_waiver_not_applied_under_200():
    # waiver True but total 55 <= 200 -> no deduction (branch 33->36)
    result = calculate_water_bill([make_account([30], leak_waiver=True)], 10.0)
    assert result["total_billed"] == 55.0


def test_leak_waiver_boundary_exactly_200():
    # 200.0 is not > 200.0 -> no deduction
    # base 50 + 100*1.5 = 200
    result = calculate_water_bill([make_account([50, 50], leak_waiver=True)], 50.0)
    assert result["total_billed"] == 200.0


# --- status: `if flagged > 5` / `elif total == 0.0` / NORMAL ---

def test_status_excessive_flags():
    result = calculate_water_bill([make_account([0, -1, 0, -2, 0, -3])], 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_status_exactly_five_flags_is_normal():
    # boundary: 5 is not > 5
    result = calculate_water_bill([make_account([0, -1, 0, -2, 0])], 10.0)
    assert result["status"] == "NORMAL"


def test_flags_counted_across_accounts():
    # 3 flags in each account -> 6 total
    accounts = [make_account([0, 0, 0]), make_account([-1, -1, -1])]
    assert calculate_water_bill(accounts, 10.0)["status"] == "EXCESSIVE_FLAGS"


def test_excessive_flags_takes_priority_over_no_activity():
    # total is 0 but flags > 5 -> first branch wins
    result = calculate_water_bill([make_account([0, 0, 0, 0, 0, 0])], 0.0)
    assert result == {"total_billed": 0.0, "status": "EXCESSIVE_FLAGS"}


def test_status_normal():
    result = calculate_water_bill([make_account([30])], 10.0)
    assert result["status"] == "NORMAL"


# ============ check_meter_tampering ============

def test_tampering_no_data_empty_list():
    assert check_meter_tampering([]) == "NO_DATA"


def test_tampering_no_data_none():
    assert check_meter_tampering(None) == "NO_DATA"


def test_meter_with_no_readings_is_clear():
    # inner loop not entered
    assert check_meter_tampering([[]]) == "CLEAR"


def test_all_positive_readings_clear():
    assert check_meter_tampering([[1, 2, 3]]) == "CLEAR"


def test_zero_delta_counts_as_forward():
    # 0 is not < 0 -> resets counter
    assert check_meter_tampering([[-1, 0, -1]]) == "CLEAR"


def test_single_negatives_reset_by_positive_clear():
    # negative but count < 2, then reset by positive (both inner branches)
    assert check_meter_tampering([[-1, 2, -1, 3]]) == "CLEAR"


def test_single_trailing_negative_clear():
    assert check_meter_tampering([[3, -1]]) == "CLEAR"


def test_two_consecutive_negatives_tamper():
    assert check_meter_tampering([[5, -1, -2]]) == "TAMPER_SUSPECTED"


def test_tamper_found_on_later_meter():
    # first meter clear, outer loop moves on, second meter tampered
    assert check_meter_tampering([[1, 2], [4, -1, -1]]) == "TAMPER_SUSPECTED"


def test_counter_resets_between_meters():
    # negative at end of meter 1 + negative at start of meter 2 is NOT consecutive
    assert check_meter_tampering([[1, -1], [-1, 2]]) == "CLEAR"
