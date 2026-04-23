from risk_rules import label_risk, score_transaction


BASE_TX = {
    "device_risk_score": 10,
    "is_international": 0,
    "amount_usd": 100,
    "velocity_24h": 1,
    "failed_logins_24h": 0,
    "prior_chargebacks": 0,
}


def tx(**overrides):
    return {**BASE_TX, **overrides}


def test_label_risk_thresholds():
    assert label_risk(10) == "low"
    assert label_risk(35) == "medium"
    assert label_risk(75) == "high"


def test_large_amount_adds_risk():
    assert score_transaction(tx(amount_usd=1200)) >= 25


def test_high_risk_device_adds_risk():
    low = score_transaction(tx(device_risk_score=10))
    high = score_transaction(tx(device_risk_score=80))
    assert high > low


def test_medium_risk_device_adds_risk():
    low = score_transaction(tx(device_risk_score=10))
    mid = score_transaction(tx(device_risk_score=50))
    assert mid > low


def test_international_adds_risk():
    domestic = score_transaction(tx(is_international=0))
    international = score_transaction(tx(is_international=1))
    assert international > domestic


def test_high_velocity_adds_risk():
    low_vel = score_transaction(tx(velocity_24h=1))
    high_vel = score_transaction(tx(velocity_24h=8))
    assert high_vel > low_vel


def test_medium_velocity_adds_risk():
    low_vel = score_transaction(tx(velocity_24h=1))
    mid_vel = score_transaction(tx(velocity_24h=4))
    assert mid_vel > low_vel


def test_prior_chargebacks_add_risk():
    none = score_transaction(tx(prior_chargebacks=0))
    one = score_transaction(tx(prior_chargebacks=1))
    two = score_transaction(tx(prior_chargebacks=2))
    assert one > none
    assert two > one


def test_failed_logins_add_risk():
    none = score_transaction(tx(failed_logins_24h=0))
    some = score_transaction(tx(failed_logins_24h=3))
    many = score_transaction(tx(failed_logins_24h=6))
    assert some > none
    assert many > some


def test_score_clamped_between_0_and_100():
    worst = score_transaction(tx(
        device_risk_score=90,
        is_international=1,
        amount_usd=2000,
        velocity_24h=10,
        failed_logins_24h=10,
        prior_chargebacks=3,
    ))
    assert 0 <= worst <= 100


def test_max_risk_profile_is_high():
    worst = score_transaction(tx(
        device_risk_score=90,
        is_international=1,
        amount_usd=2000,
        velocity_24h=10,
        failed_logins_24h=10,
        prior_chargebacks=3,
    ))
    assert label_risk(worst) == "high"
