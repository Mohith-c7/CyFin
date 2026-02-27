import unittest
import sys

with open('stress_errors.txt', 'w', encoding='utf-8') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    suite = unittest.TestLoader().discover('.', pattern='test_stress_simulation_engine.py')
    runner.run(suite)

with open('explain_errors.txt', 'w', encoding='utf-8') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    suite = unittest.TestLoader().discover('.', pattern='test_explainability_engine.py')
    runner.run(suite)
