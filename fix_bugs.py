import pathlib, re

# --- Fix 1: dashboard_service.py – remove timeline[:15] slice ---------------
ds = pathlib.Path('backend/app/services/dashboard_service.py')
text = ds.read_text(encoding='utf-8')
old = '"recent_timeline": timeline[:15],'
new = '"recent_timeline": timeline,'
if old in text:
    text = text.replace(old, new)
    ds.write_text(text, encoding='utf-8')
    print('FIX 1 APPLIED: dashboard_service.py - removed timeline[:15] slice')
else:
    print('FIX 1: pattern not found -', repr(old[:60]))

# --- Fix 2: intelligence.py – call run_safety_check before get_patient_alerts -
intel = pathlib.Path('backend/app/api/v1/intelligence.py')
text2 = intel.read_text(encoding='utf-8')
old2 = '''    """All medication interaction alerts for a patient (newest first)."""
    await _verify_patient_access(patient_id, current_user, db)
    return await safety_service.get_patient_alerts(patient_id, db)'''
new2 = '''    """All medication interaction alerts for a patient (newest first)."""
    await _verify_patient_access(patient_id, current_user, db)
    # Run safety check to generate any new alerts, then return all
    await safety_service.run_safety_check(patient_id, db)
    await db.commit()
    return await safety_service.get_patient_alerts(patient_id, db)'''
if old2 in text2:
    text2 = text2.replace(old2, new2)
    intel.write_text(text2, encoding='utf-8')
    print('FIX 2 APPLIED: intelligence.py - alerts endpoint now runs safety check first')
else:
    print('FIX 2: pattern not found')

# --- Fix 3: dashboard_service.py – run_safety_check then get_patient_alerts --
ds2 = pathlib.Path('backend/app/services/dashboard_service.py')
text3 = ds2.read_text(encoding='utf-8')
old3 = '    alerts = await safety_service.get_patient_alerts(patient_id, db)'
new3 = '''    await safety_service.run_safety_check(patient_id, db)
    alerts = await safety_service.get_patient_alerts(patient_id, db)'''
if old3 in text3:
    text3 = text3.replace(old3, new3)
    ds2.write_text(text3, encoding='utf-8')
    print('FIX 3 APPLIED: dashboard_service.py - run_safety_check before get_patient_alerts')
else:
    print('FIX 3: pattern not found')
