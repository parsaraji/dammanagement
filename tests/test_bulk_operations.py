from app.models.animal import Animal, Species
from app.models.medical import Vaccination
from app.models.measurement import Measurement

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

def test_batch_submit_transaction(auth_client):
    animals = Animal.query.filter_by(species=Species.SHEEP).limit(2).all()
    assert len(animals) == 2

    a1, a2 = animals[0], animals[1]

    # Batch submit: vaccination for a1, weight measurement for a2
    res = auth_client.post('/bulk-operations/batch-submit', data={
        'batch_animal_id[]': [str(a1.id), str(a2.id)],
        'batch_op_type[]': ['vaccine', 'weight'],
        'batch_date[]': ['1402/08/10', '1402/08/10'],
        'batch_p1[]': ['آنتروتوکسمی', '45.5'],
        'batch_p2[]': ['دوز ۱', '']
    }, follow_redirects=True)

    assert res.status_code == 200
    v = Vaccination.query.filter_by(animal_id=a1.id, vaccine_name='آنتروتوکسمی').first()
    assert v is not None

    m = Measurement.query.filter_by(animal_id=a2.id, value=45.5).first()
    assert m is not None
