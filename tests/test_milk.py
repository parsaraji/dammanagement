from datetime import date
from app.models.animal import Animal
from app.services.milk_service import compute_standardized_milk, calculate_4pct_fcm, compute_tim_cumulative_yield

def test_milk_standardization(app):
    with app.app_context():
        # Well populated female (IR-G1-F2)
        female_well = Animal.query.filter_by(plastic_tag='IR-G1-F2').first()
        res_well = compute_standardized_milk(female_well.id, female_well.parity or 1)
        assert res_well['success'] is True
        assert res_well['avg'] > 0
        assert 'tim_cumulative' in res_well

        # Sparse female (IR-G1-F1)
        female_sparse = Animal.query.filter_by(plastic_tag='IR-G1-F1').first()
        res_sparse = compute_standardized_milk(female_sparse.id, female_sparse.parity or 1)
        assert res_sparse['success'] is False
        assert 'کافی نیست' in res_sparse['message']

def test_icar_tim_cumulative_yield_formula():
    class DummyRecord:
        def __init__(self, dt, amt):
            self.date = dt
            self.total_amount = amt

    r1 = DummyRecord(date(2023, 1, 1), 3.0)
    r2 = DummyRecord(date(2023, 1, 11), 5.0)  # 10 days gap

    # Interval yield = ((3.0 + 5.0)/2) * 10 = 40.0 kg
    tim_yield = compute_tim_cumulative_yield([r1, r2])
    assert tim_yield == 40.0

def test_gaines_4pct_fcm_formula():
    # 10 kg milk with 4.0% fat -> FCM = (0.4 * 10) + (15 * (10 * 0.04)) = 4 + 6 = 10 kg
    fcm = calculate_4pct_fcm(10.0, 4.0)
    assert fcm == 10.0

    # 10 kg milk with 5.0% fat -> FCM = 4 + (15 * 0.5) = 11.5 kg
    fcm_high_fat = calculate_4pct_fcm(10.0, 5.0)
    assert fcm_high_fat == 11.5

def test_milk_bulk_submit_route(client, app):
    with app.app_context():
        # Login
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'

        female = Animal.query.filter_by(plastic_tag='IR-G1-F2').first()
        res = client.post('/milk-bulk/submit', data={
            'date': '1402/08/15',
            'record_type': 'official',
            'animal_id[]': [str(female.id)],
            'm1[]': ['2.5'],
            'm2[]': ['2.0'],
            'm3[]': ['0.0']
        }, follow_redirects=True)

        assert res.status_code == 200
        assert b'Bad Request' not in res.data
        assert b'CSRF token is missing' not in res.data
