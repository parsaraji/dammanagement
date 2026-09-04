from app.models.animal import Animal, AnimalStatus

def test_create_animal(auth_client):
    data = {
        'plastic_tag': 'TEST-EW-01',
        'serial_number': 'TEST-SN-01',
        'birth_date': '1402/01/01',
        'sex': 'female',
        'species': 'sheep',
        'breed': 'افشاری',
        'parity': 1,
        'origin': 'born_in_farm'
    }
    res = auth_client.post('/animals/new', data=data)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True

    animal = Animal.query.filter_by(plastic_tag='TEST-EW-01').first()
    assert animal is not None
    assert animal.species.name == 'SHEEP' or animal.species.value == 'sheep'

def test_soft_delete_removal(auth_client):
    animal = Animal.query.filter_by(plastic_tag='IR-G2-INB1').first()
    assert animal is not None

    res = auth_client.post(f'/animals/{animal.id}/remove', data={
        'removal_date': '1402/08/01',
        'removal_reason': 'فروش پروار'
    })
    assert res.status_code == 200

    # Verify soft delete
    updated_animal = Animal.query.get(animal.id)
    assert updated_animal.status == AnimalStatus.REMOVED
    assert updated_animal.removal_reason == 'فروش پروار'
