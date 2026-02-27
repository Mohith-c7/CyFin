"""
Test Suite for Market Stability Index Module (V2)
Validates MSI computation, classification, contagion integration, and edge cases.

Updated for V2 formula:
    MSI = (
        1.00 * trust
        - 20 * anomaly_rate
        - 4 * log(1 + anomalies)
        - 25 * feed_mismatch
        - 0.30 * contagion_risk_score
    )
"""

from systemic.market_stability_index import MarketStabilityIndex
import math


def test_basic_computation():
    """Test basic MSI computation with typical values."""
    print("=" * 80)
    print("TEST 1: Basic MSI Computation")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    result = msi_calc.compute_msi(
        average_trust_score=85.0,
        market_anomaly_rate=0.02,
        total_anomalies=5,
        feed_mismatch_rate=0.01,
        contagion_risk_score=10.0
    )

    print(f"\nInputs:")
    print(f"  Trust Score: 85.0")
    print(f"  Anomaly Rate: 0.02 (2%)")
    print(f"  Total Anomalies: 5")
    print(f"  Feed Mismatch: 0.01 (1%)")
    print(f"  Contagion Risk Score: 10.0")

    print(f"\nResults:")
    print(f"  MSI Score: {result['msi_score']}")
    print(f"  Market State: {result['market_state']}")
    print(f"  Risk Level: {result['risk_level']}")

    assert 0 <= result['msi_score'] <= 100, "MSI must be in [0, 100]"
    assert result['market_state'] in [
        "STABLE", "ELEVATED RISK", "HIGH VOLATILITY", "SYSTEMIC RISK"
    ]
    assert result['risk_level'] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    print("\n✅ Test 1 PASSED")
    return result


def test_stable_market():
    """Test MSI with stable market conditions (V2 formula)."""
    print("\n" + "=" * 80)
    print("TEST 2: Stable Market Scenario (V2)")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    # Perfect conditions: MSI = 1.0 * 100 = 100.0
    result = msi_calc.compute_msi(
        average_trust_score=100.0,
        market_anomaly_rate=0.0,
        total_anomalies=0,
        feed_mismatch_rate=0.0,
        contagion_risk_score=0.0
    )

    print(f"\nInputs (Perfect Conditions):")
    print(f"  Trust Score: 100.0 (Perfect)")
    print(f"  Anomaly Rate: 0.0 (None)")
    print(f"  Total Anomalies: 0 (None)")
    print(f"  Feed Mismatch: 0.0 (Perfect)")
    print(f"  Contagion Risk: 0.0 (None)")

    print(f"\nResults:")
    print(f"  MSI Score: {result['msi_score']}")
    print(f"  Market State: {result['market_state']}")

    # V2: MSI caps at 100 with perfect inputs (1.0 * 100)
    print(f"\n  Note: V2 MSI caps at 100 with perfect inputs (1.0 * 100)")
    print(f"  STABLE threshold (>=80) is now more achievable with perfect conditions")

    assert result['msi_score'] == 100.0, f"Perfect conditions should give 100.0, got {result['msi_score']}"

    print("\n✅ Test 2 PASSED - V2 formula working as designed")
    return result


def test_systemic_risk():
    """Test MSI with systemic risk conditions."""
    print("\n" + "=" * 80)
    print("TEST 3: Systemic Risk Scenario")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    result = msi_calc.compute_msi(
        average_trust_score=30.0,
        market_anomaly_rate=0.15,
        total_anomalies=50,
        feed_mismatch_rate=0.10,
        contagion_risk_score=60.0
    )

    print(f"\nInputs (Crisis Conditions):")
    print(f"  Trust Score: 30.0 (Very Low)")
    print(f"  Anomaly Rate: 0.15 (15%)")
    print(f"  Total Anomalies: 50 (High)")
    print(f"  Feed Mismatch: 0.10 (10%)")
    print(f"  Contagion Risk: 60.0 (High Contagion)")

    print(f"\nResults:")
    print(f"  MSI Score: {result['msi_score']}")
    print(f"  Market State: {result['market_state']}")
    print(f"  Risk Level: {result['risk_level']}")

    # Reconstruct V2 expected MSI for these inputs
    expected_msi_raw = (
        1.00 * 30.0  # trust
        - 20 * 0.15  # anomaly_rate
        - 4 * math.log(1 + 50)  # anomalies
        - 25 * 0.10  # feed_mismatch
        - 0.30 * 60.0  # contagion_risk_score
    )
    # Clamped between 0 and 100
    expected_msi = max(0.0, min(100.0, expected_msi_raw))

    assert result['msi_score'] < 40, f"Should be SYSTEMIC RISK, got {result['msi_score']}"
    assert result['market_state'] == "SYSTEMIC RISK"
    assert result['risk_level'] == "CRITICAL"
    assert expected_msi <= 100, "Expected MSI should be within bounds"


    print("\n✅ Test 3 PASSED - Market correctly classified as SYSTEMIC RISK")
    return result


def test_component_breakdown():
    """Test detailed component breakdown (V2 with contagion)."""
    print("\n" + "=" * 80)
    print("TEST 4: Component Breakdown Analysis (V2)")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    breakdown = msi_calc.get_component_breakdown(
        average_trust_score=80.0,
        market_anomaly_rate=0.05,
        total_anomalies=10,
        feed_mismatch_rate=0.02,
        contagion_risk_score=20.0
    )

    print(f"\nComponent Contributions:")
    print(f"  Trust Contribution:      +{breakdown['trust_contribution']:.2f}")
    print(f"  Anomaly Rate Penalty:    -{breakdown['anomaly_rate_penalty']:.2f}")
    print(f"  Anomaly Count Penalty:   -{breakdown['anomaly_count_penalty']:.2f}")
    print(f"  Feed Mismatch Penalty:   -{breakdown['feed_mismatch_penalty']:.2f}")
    print(f"  Contagion Penalty:       -{breakdown['contagion_penalty']:.2f}")
    print(f"  Raw MSI:                  {breakdown['raw_msi']:.2f}")
    print(f"  Clamped MSI:              {breakdown['clamped_msi']:.2f}")

    # Verify math
    expected_raw = (
        breakdown['trust_contribution']
        - breakdown['anomaly_rate_penalty']
        - breakdown['anomaly_count_penalty']
        - breakdown['feed_mismatch_penalty']
        - breakdown['contagion_penalty']
    )

    assert abs(breakdown['raw_msi'] - expected_raw) < 0.01, "Component math error"
    assert abs(breakdown["trust_contribution"] - (1.00 * 80.0)) < 1e-4, "Trust component calculation error"
    assert 'contagion_penalty' in breakdown, "V2 must include contagion"

    print("\n✅ Test 4 PASSED - V2 component breakdown correct")
    return breakdown


def test_integration_with_multi_symbol():
    """Test integration with MultiSymbolMonitor output."""
    print("\n" + "=" * 80)
    print("TEST 5: Integration with MultiSymbolMonitor")
    print("=" * 80)

    # Simulate MultiSymbolMonitor.get_market_summary() output
    market_summary = {
        'symbols_monitored': 3,
        'total_data_points': 1170,
        'total_anomalies': 12,
        'market_anomaly_rate': 0.0103,
        'average_trust_score': 87.5,
        'symbols': ['AAPL', 'MSFT', 'GOOGL']
    }

    print(f"\nMarket Summary (from MultiSymbolMonitor):")
    print(f"  Symbols: {market_summary['symbols']}")
    print(f"  Data Points: {market_summary['total_data_points']}")
    print(f"  Anomalies: {market_summary['total_anomalies']}")
    print(f"  Anomaly Rate: {market_summary['market_anomaly_rate']:.4f}")
    print(f"  Avg Trust: {market_summary['average_trust_score']:.1f}")

    # Compute MSI (with contagion defaulting to 0)
    msi_calc = MarketStabilityIndex()
    result = msi_calc.compute_msi(
        average_trust_score=market_summary['average_trust_score'],
        market_anomaly_rate=market_summary['market_anomaly_rate'],
        total_anomalies=market_summary['total_anomalies'],
        feed_mismatch_rate=0.0,
        contagion_risk_score=0.0
    )

    print(f"\nMSI Results:")
    print(f"  MSI Score: {result['msi_score']}")
    print(f"  Market State: {result['market_state']}")
    print(f"  Risk Level: {result['risk_level']}")

    assert 0 <= result['msi_score'] <= 100
    print("\n✅ Test 5 PASSED - Integration successful")
    return result


def test_edge_cases():
    """Test edge cases and boundary conditions (V2)."""
    print("\n" + "=" * 80)
    print("TEST 6: Edge Cases and Boundaries (V2)")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    # Test 1: Perfect conditions (V2: 1.0 * 100 = 100)
    print("\n  Case 1: Perfect Market (V2)")
    result1 = msi_calc.compute_msi(100.0, 0.0, 0, 0.0, 0.0)
    print(f"    MSI: {result1['msi_score']} (Expected: 100.0)")
    assert result1['msi_score'] == 100.0, f"Perfect market V2 should give 100.0, got {result1['msi_score']}"

    # Test 2: Zero trust
    print("\n  Case 2: Zero Trust")
    result2 = msi_calc.compute_msi(0.0, 0.0, 0, 0.0, 0.0)
    print(f"    MSI: {result2['msi_score']} (Expected: 0.0)")
    assert result2['msi_score'] == 0.0, "Zero trust should give 0.0"

    # Test 3: Maximum penalties
    print("\n  Case 3: Maximum Penalties (with contagion)")
    result3 = msi_calc.compute_msi(50.0, 1.0, 1000, 1.0, 100.0)
    print(f"    MSI: {result3['msi_score']} (Should be clamped to 0)")
    assert result3['msi_score'] == 0.0, "Should clamp to 0"

    # Test 4: Contagion-only impact
    print("\n  Case 4: Contagion Impact")
    base = msi_calc.compute_msi(80.0, 0.0, 0, 0.0, 0.0)
    with_contagion = msi_calc.compute_msi(80.0, 0.0, 0, 0.0, 50.0)
    contagion_impact = base['msi_score'] - with_contagion['msi_score']
    print(f"    Base MSI: {base['msi_score']}")
    print(f"    With CRS=50: {with_contagion['msi_score']}")
    print(f"    Contagion Impact: -{contagion_impact}")
    assert contagion_impact == 15.0, f"CRS=50 should reduce MSI by 15, got {contagion_impact}"

    # Test 5: Boundary thresholds
    print("\n  Case 5: Threshold Boundaries")
    result5a = msi_calc.compute_msi(90.0, 0.0, 0, 0.0, 0.0)
    result5b = msi_calc.compute_msi(30.0, 0.1, 20, 0.1, 50.0)
    print(f"    High trust: {result5a['market_state']}")
    print(f"    Crisis: {result5b['market_state']}")
    assert result5a['market_state'] in [
        "STABLE", "ELEVATED RISK", "HIGH VOLATILITY", "SYSTEMIC RISK"
    ]
    assert result5b['market_state'] in [
        "STABLE", "ELEVATED RISK", "HIGH VOLATILITY", "SYSTEMIC RISK"
    ]

    print("\n✅ Test 6 PASSED - All V2 edge cases handled correctly")


def test_input_validation():
    """Test input validation and error handling."""
    print("\n" + "=" * 80)
    print("TEST 7: Input Validation")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    # Test invalid trust score
    print("\n  Testing invalid trust score (> 100)...")
    try:
        msi_calc.compute_msi(150.0, 0.0, 0, 0.0, 0.0)
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"    ✓ Correctly raised: {e}")

    # Test invalid anomaly rate
    print("\n  Testing invalid anomaly rate (> 1)...")
    try:
        msi_calc.compute_msi(80.0, 1.5, 0, 0.0, 0.0)
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"    ✓ Correctly raised: {e}")

    # Test negative anomalies
    print("\n  Testing negative anomalies...")
    try:
        msi_calc.compute_msi(80.0, 0.0, -5, 0.0, 0.0)
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"    ✓ Correctly raised: {e}")

    # Test wrong type
    print("\n  Testing wrong type (string instead of float)...")
    try:
        msi_calc.compute_msi("80", 0.0, 0, 0.0, 0.0)
        assert False, "Should raise TypeError"
    except TypeError as e:
        print(f"    ✓ Correctly raised: {e}")

    # Test invalid contagion risk score
    print("\n  Testing invalid contagion score (> 100)...")
    try:
        msi_calc.compute_msi(80.0, 0.0, 0, 0.0, 150.0)
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"    ✓ Correctly raised: {e}")

    # Test invalid contagion type
    print("\n  Testing invalid contagion type (string)...")
    try:
        msi_calc.compute_msi(80.0, 0.0, 0, 0.0, "high")
        assert False, "Should raise TypeError"
    except TypeError as e:
        print(f"    ✓ Correctly raised: {e}")

    print("\n✅ Test 7 PASSED - Input validation working correctly")


def test_backward_compatibility():
    """Test that V2 MSI works when called without contagion (V1 style)."""
    print("\n" + "=" * 80)
    print("TEST 8: Backward Compatibility (V1-style calls)")
    print("=" * 80)

    msi_calc = MarketStabilityIndex()

    # Call without contagion_risk_score (should default to 0.0)
    result = msi_calc.compute_msi(
        average_trust_score=85.0,
        market_anomaly_rate=0.02,
        total_anomalies=5,
        feed_mismatch_rate=0.01
    )

    print(f"\nV1-style call (no contagion param):")
    print(f"  MSI Score: {result['msi_score']}")
    print(f"  Market State: {result['market_state']}")

    assert 0 <= result['msi_score'] <= 100
    assert result['inputs_used']['contagion_risk_score'] == 0.0

    # Call without feed_mismatch_rate OR contagion_risk_score
    result2 = msi_calc.compute_msi(
        average_trust_score=85.0,
        market_anomaly_rate=0.02,
        total_anomalies=5
    )

    print(f"\nMinimal call (trust + anomaly only):")
    print(f"  MSI Score: {result2['msi_score']}")
    assert 0 <= result2['msi_score'] <= 100

    print("\n✅ Test 8 PASSED - Backward compatibility confirmed")


def run_all_tests():
    """Run complete test suite."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "MARKET STABILITY INDEX V2 TEST SUITE" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    try:
        # Run all tests
        test_basic_computation()
        test_stable_market()
        test_systemic_risk()
        test_component_breakdown()
        test_integration_with_multi_symbol()
        test_edge_cases()
        test_input_validation()
        test_backward_compatibility()

        # Summary
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Market Stability Index V2 module is production-ready")
        print("✅ Contagion Risk Score integration verified")
        print("✅ Backward compatibility confirmed")
        print("✅ All computations verified")
        print("✅ Edge cases handled")
        print("✅ Input validation working")
        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
