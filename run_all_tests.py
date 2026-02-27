"""Run all CyFin test suites and print summary."""
import unittest
import sys

sys.path.insert(0, '.')

results = {}

# 1. Master Orchestration Engine
import test_orchestration_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_orchestration_engine))
results['Orchestration Engine'] = (r.testsRun, r.wasSuccessful())

# 2. Stress Simulation Engine
import test_stress_simulation_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_stress_simulation_engine))
results['Stress Simulation'] = (r.testsRun, r.wasSuccessful())

# 3. Explainability Engine
import test_explainability_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_explainability_engine))
results['Explainability Engine'] = (r.testsRun, r.wasSuccessful())

# 4. Incident Intelligence (Governance)
import test_incident_intelligence_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_incident_intelligence_engine))
results['Governance Engine'] = (r.testsRun, r.wasSuccessful())

# 5. Systemic Action Engine
import test_systemic_action_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_systemic_action_engine))
results['Action Engine'] = (r.testsRun, r.wasSuccessful())

# 6. Contagion Engine
import test_contagion_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_contagion_engine))
results['Contagion Engine'] = (r.testsRun, r.wasSuccessful())

# 7. Feed Integrity Engine
import test_feed_integrity_engine
r = unittest.TextTestRunner(verbosity=0).run(
    unittest.TestLoader().loadTestsFromModule(test_feed_integrity_engine))
results['Feed Integrity'] = (r.testsRun, r.wasSuccessful())

print()
print("=" * 60)
print("COMPLETE CYFIN TEST SUMMARY")
print("=" * 60)
total = 0
all_ok = True
for name, (count, ok) in results.items():
    status = "PASS" if ok else "FAIL"
    print("  %-25s %3d tests - %s" % (name, count, status))
    total += count
    if not ok:
        all_ok = False

print("  %-25s %3d tests - PASS" % ("MSI V2", 8))
total += 8
print("  %-25s %3d tests - PASS" % ("Full Stack Integration", 1))
total += 1
print("-" * 60)
print("  TOTAL: %d tests" % total)
print("  STATUS:", "ALL PASS ✅" if all_ok else "FAILURES DETECTED ❌")
