import pytest
from hospital_triage_priority import process_triage_wards, monitor_oxygen_manifolds

# ============================================================================
# Branch Coverage Tests for hospital_triage_priority.py
# Targets 100% Branch Coverage across all decision paths
# ============================================================================

def test_branch_validation_wards_not_list():
    # Branch: not isinstance(wards, list) is True
    with pytest.raises(ValueError, match="Invalid wards list or base acuity score"):
        process_triage_wards("not_a_list", 10)

def test_branch_validation_negative_acuity():
    # Branch: default_acuity_score < 0 is True
    with pytest.raises(ValueError, match="Invalid wards list or base acuity score"):
        process_triage_wards([], -1)

def test_branch_ward_not_accepting():
    # Branch: not ward.get("is_accepting", False) evaluates to True (ward skipped)
    wards = [
        {"is_accepting": False, "tier": "general", "patients": [{"spo2": 95, "hr": 75}]},
        {"is_accepting": True, "tier": "general", "patients": [{"spo2": 96, "hr": 70}]}
    ]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 10, "status": "TRIAGE_STABLE"}

def test_branch_patient_invalid_spo2():
    # Branch: spo2 <= 0 evaluates to True
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 0, "hr": 75}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}

def test_branch_patient_invalid_heart_rate():
    # Branch: heart_rate <= 0 evaluates to True (spo2 > 0)
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": -5}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}

def test_branch_unconscious_outpatient_tier():
    # Branch: is_unconscious True, ward_tier == 'outpatient' (triggers break and resets acuity)
    wards = [{
        "is_accepting": True,
        "tier": "outpatient",
        "patients": [
            {"spo2": 95, "hr": 75, "unconscious": True},
            {"spo2": 95, "hr": 75, "unconscious": False}  # unreachable after break
        ]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}

def test_branch_unconscious_non_outpatient():
    # Branch: is_unconscious True, ward_tier != 'outpatient' (+100 acuity)
    wards = [{
        "is_accepting": True,
        "tier": "icu",
        "patients": [{"spo2": 95, "hr": 75, "unconscious": True}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 100, "status": "TRIAGE_STABLE"}

def test_branch_spo2_low_critical():
    # Branch: spo2 < 90 evaluates to True (+60 acuity)
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 88, "hr": 75, "unconscious": False}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 60, "status": "TRIAGE_STABLE"}

def test_branch_heart_rate_high_critical():
    # Branch: heart_rate > 120 evaluates to True (spo2 >= 90) (+60 acuity)
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 135, "unconscious": False}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 60, "status": "TRIAGE_STABLE"}

def test_branch_normal_patient_vitals():
    # Branch: neither critical nor unconscious (default acuity added)
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 98, "hr": 80, "unconscious": False}]
    }]
    result = process_triage_wards(wards, 15)
    assert result == {"acuity_score": 15, "status": "TRIAGE_STABLE"}

def test_branch_icu_standby_flag():
    # Branch: icu_standby is True (+25 acuity)
    wards = [{
        "is_accepting": True,
        "icu_standby": True,
        "patients": [{"spo2": 95, "hr": 75}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 35, "status": "TRIAGE_STABLE"}

def test_branch_ward_alert_flagged_greater_than_4():
    # Branch: flagged_entries > 4 evaluates to True
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": -1, "hr": 70},
            {"spo2": 95, "hr": -1},
            {"spo2": 0, "hr": 0},
            {"spo2": 95, "hr": 75, "unconscious": True},
            {"spo2": 95, "hr": 75, "unconscious": True}
        ]
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"

def test_branch_oxygen_no_data():
    # Branch: not sensor_streams evaluates to True
    assert monitor_oxygen_manifolds([]) == "NO_DATA"
    assert monitor_oxygen_manifolds(None) == "NO_DATA"

def test_branch_oxygen_pressure_failure():
    # Branch: pressure_bar < 4.0 and drop_streak >= 2 evaluates to True
    sensor_streams = [[5.0, 3.8, 3.5]]
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_FAILURE"

def test_branch_oxygen_streak_reset_and_normal():
    # Branch: pressure_bar >= 4.0 resets drop_streak to 0
    sensor_streams = [[3.9, 4.5, 3.8, 4.2]]
    assert monitor_oxygen_manifolds(sensor_streams) == "PRESSURE_NORMAL"
