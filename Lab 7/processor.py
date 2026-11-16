import math

def parse_vitals_summary(vitals_csv):
    if not isinstance(vitals_csv, str):
        return "Invalid vitals input: input must be a string"
    parts = [p.strip() for p in vitals_csv.split(',')]
    if len(parts) != 3:
        return "Invalid vitals format: expected HR,SpO2,Temp"
    try:
        hr = float(parts[0])
        spo2 = float(parts[1])
        temp = float(parts[2])
    except (ValueError, TypeError):
        return "Invalid vitals numeric values"

    if math.isnan(hr) or math.isnan(spo2) or math.isnan(temp) or \
       math.isinf(hr) or math.isinf(spo2) or math.isinf(temp):
        return "Invalid vitals: values cannot be NaN or Infinite"

    if hr <= 0 or spo2 < 0 or spo2 > 100 or temp <= 0:
        return "Invalid vitals out of physiological range"

    critical = hr > 120 or spo2 < 90 or temp > 39.0
    return f"Vitals: HR={hr}, SpO2={spo2}% - {'CRITICAL' if critical else 'STABLE'}"

def compute_patient_bmi(bmi_string):
    if not isinstance(bmi_string, str):
        return None
    parts = bmi_string.strip().split('/')
    if len(parts) != 2:
        return None
    try:
        weight = float(parts[0])
        height = float(parts[1])
    except (ValueError, TypeError):
        return None

    if math.isnan(weight) or math.isnan(height) or math.isinf(weight) or math.isinf(height):
        return None
    if weight <= 0 or height <= 0:
        return None

    try:
        bmi = weight / (height ** 2)
        if math.isnan(bmi) or math.isinf(bmi):
            return None
        return round(bmi, 2)
    except (ZeroDivisionError, OverflowError):
        return None

def assign_ward_bed(allocation_code):
    if not isinstance(allocation_code, str):
        return "Invalid allocation input: input must be a string"
    parts = allocation_code.strip().split('-')
    if len(parts) != 2:
        return "Invalid allocation format: expected WARD-BED"

    ward_names = {
        "ER": "Emergency Room",
        "ICU": "Intensive Care Unit",
        "GEN": "General Ward",
        "PED": "Pediatrics"
    }
    ward = parts[0].strip().upper()
    bed_str = parts[1].strip()

    if ward not in ward_names:
        return f"Invalid ward code '{ward}'. Valid wards: ER, ICU, GEN, PED"

    try:
        bed_num = int(bed_str)
        if bed_num <= 0:
            return "Invalid bed number: must be positive"
    except (ValueError, TypeError):
        return "Invalid bed number: must be an integer"

    return f"{ward_names[ward]} Bed #{bed_num}"

def main():
    print("==== Running parse_vitals_summary ====")
    v_input = input("Enter vitals (HR,SpO2,Temp): ")
    print("Summary:", parse_vitals_summary(v_input))

    print("\n==== Running compute_patient_bmi ====")
    b_input = input("Enter weight/height (e.g. 70/1.75): ")
    print("BMI:", compute_patient_bmi(b_input))

    print("\n==== Running assign_ward_bed ====")
    w_input = input("Enter allocation (e.g. ICU-05): ")
    print("Assignment:", assign_ward_bed(w_input))

if __name__ == "__main__":
    main()
