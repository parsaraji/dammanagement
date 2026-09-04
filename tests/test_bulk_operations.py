from app.models.medical import Vaccination

def test_bulk_vaccination_apply(auth_client):
    # Select animals first
    auth_client.post('/bulk-operations/select', data={'species': 'sheep'})

    # Apply quick vaccination
    res = auth_client.post('/bulk-operations/quick-apply', data={
        'op_type': 'vaccination',
        'date': '1402/08/01',
        'detail': 'تب برفکی'
    }, follow_redirects=True)
    assert res.status_code == 200

    vac_count = Vaccination.query.filter_by(vaccine_name='تب برفکی').count()
    assert vac_count > 0
