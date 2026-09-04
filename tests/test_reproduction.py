from app.models.animal import Animal
from app.models.reproduction import Insemination, Calving

def test_full_reproduction_flow(auth_client):
    animal = Animal.query.filter_by(plastic_tag='IR-G1-F1').first()
    assert animal is not None

    # CIDR
    res = auth_client.post(f'/reproduction/{animal.id}/cidr', data={
        'insert_date': '1402/01/01',
        'remove_date': '1402/01/14',
        'cidr_type': 'EAZI'
    })
    assert res.get_json()['success'] is True

    # Insemination
    res = auth_client.post(f'/reproduction/{animal.id}/insemination', data={
        'date': '1402/01/16',
        'insemination_type': 'artificial',
        'led_to_pregnancy': 'y'
    })
    assert res.get_json()['success'] is True

    # Calving
    res = auth_client.post(f'/reproduction/{animal.id}/calving', data={
        'date': '1402/06/16',
        'calving_type': 'normal',
        'offspring_count': 2
    })
    json_data = res.get_json()
    assert json_data['success'] is True
    assert json_data['open_newborn_modal'] is True
    assert json_data['newborn_data']['count'] == 2
