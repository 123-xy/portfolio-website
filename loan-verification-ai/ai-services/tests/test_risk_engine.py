from ai_services.risk_engine.engine import RiskInputs, assess_risk


def test_all_strong_signals_yield_low_risk() -> None:
    result = assess_risk(
        RiskInputs(
            face_similarity=0.95,
            face_confidence=0.95,
            consent_status="explicit_yes",
            consent_confidence=0.97,
            intent_aligned=True,
            intent_confidence=0.95,
            fraud_score=0.05,
            fraud_confidence=0.9,
        )
    )
    assert result.band == "low"
    assert result.recommendation == "auto_approve_candidate"
    assert result.score < 0.33


def test_refusal_and_weak_match_yield_high_risk() -> None:
    result = assess_risk(
        RiskInputs(
            face_similarity=0.3,
            face_confidence=0.8,
            consent_status="explicit_no",
            consent_confidence=0.9,
            intent_aligned=False,
            intent_confidence=0.85,
            fraud_score=0.7,
            fraud_confidence=0.8,
        )
    )
    assert result.band == "high"
    assert result.recommendation == "high_risk_reject_candidate"
    assert result.score > 0.66


def test_ambiguous_signals_yield_medium_risk() -> None:
    result = assess_risk(
        RiskInputs(
            face_similarity=0.72,
            face_confidence=0.7,
            consent_status="ambiguous",
            consent_confidence=0.6,
            intent_aligned=True,
            intent_confidence=0.6,
            fraud_score=0.2,
            fraud_confidence=0.7,
        )
    )
    assert result.band == "medium"
    assert result.recommendation == "needs_review"


def test_missing_signals_fall_back_to_neutral_and_stay_explainable() -> None:
    result = assess_risk(RiskInputs())
    assert 0.0 <= result.score <= 1.0
    assert len(result.reasons) == 4
    assert any("unavailable" in r for r in result.reasons)


def test_component_scores_are_bounded_and_named() -> None:
    result = assess_risk(
        RiskInputs(face_similarity=0.8, consent_status="explicit_yes", consent_confidence=0.9)
    )
    assert set(result.component_scores) == {"face_match", "speech", "intent", "fraud"}
    assert all(0.0 <= v <= 1.0 for v in result.component_scores.values())


def test_custom_weights_and_thresholds_are_respected() -> None:
    # All weight on fraud; a bad fraud score alone should dominate the result.
    result = assess_risk(
        RiskInputs(face_similarity=0.99, fraud_score=0.95),
        weights={"face_match": 0.0, "speech": 0.0, "intent": 0.0, "fraud": 1.0},
        thresholds={"low_max": 0.1, "medium_max": 0.5},
    )
    assert result.score > 0.9
    assert result.band == "high"
