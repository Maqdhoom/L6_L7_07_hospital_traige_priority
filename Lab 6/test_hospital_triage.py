import pytest
from hospital_triage_priority import process_triage_wards, monitor_oxygen_manifolds

def test_single_normal_patient():
    wards = [
        {
            "is_accepting": True,
            "tier": "general",
            "icu_standby": False,
            "patients": [{"spo2": 98, "hr": 72, "unconscious": False}]
        }
    ]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10
    assert result["status"] == "TRIAGE_STABLE"

def test_invalid_wards_or_acuity():
    with pytest.raises(ValueError):
        process_triage_wards("invalid_type", 10)
    with pytest.raises(ValueError):
        process_triage_wards([], -5)

def test_ward_not_accepting():
    wards = [{"is_accepting": False, "tier": "general", "patients": [{"spo2": 95, "hr": 75}]}]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}

def test_invalid_vitals_flagged():
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": -1, "hr": 75},
            {"spo2": 95, "hr": 0}
        ]
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "NO_URGENT_CASES"

def test_unconscious_outpatient_break():
    wards = [{
        "is_accepting": True,
        "tier": "outpatient",
        "patients": [{"spo2": 95, "hr": 75, "unconscious": True}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 0, "status": "NO_URGENT_CASES"}

def test_unconscious_general_and_icu_standby():
    wards = [{
        "is_accepting": True,
        "tier": "general",
        "icu_standby": True,
        "patients": [{"spo2": 95, "hr": 75, "unconscious": True}]
    }]
    result = process_triage_wards(wards, 10)
    assert result == {"acuity_score": 125, "status": "TRIAGE_STABLE"}

def test_critical_vitals_and_normal():
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": 85, "hr": 75},
            {"spo2": 95, "hr": 130},
            {"spo2": 98, "hr": 75}
        ]
    }]
    result = process_triage_wards(wards, 15)
    assert result["acuity_score"] == 60 + 60 + 15
    assert result["status"] == "TRIAGE_STABLE"

def test_ward_alert_flagged_entries():
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": 0, "hr": 80},
            {"spo2": 95, "hr": -2},
            {"spo2": 0, "hr": 0},
            {"spo2": 95, "hr": 75, "unconscious": True},
            {"spo2": 95, "hr": 75, "unconscious": True}
        ]
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"

def test_monitor_oxygen_manifolds():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"
    assert monitor_oxygen_manifolds([[4.5, 3.5, 3.8]]) == "PRESSURE_FAILURE"
    assert monitor_oxygen_manifolds([[3.5, 4.2, 3.8, 4.0]]) == "PRESSURE_NORMAL"
