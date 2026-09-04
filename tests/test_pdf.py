from app.models.animal import Animal

def test_id_card_printable_route(auth_client):
    animal = Animal.query.first()
    assert animal is not None

    res = auth_client.get(f'/animals/{animal.id}/id-card')
    assert res.status_code == 200
    assert 'شناسنامه و کارت هویت دام'.encode('utf-8') in res.data
    assert animal.plastic_tag.encode('utf-8') in res.data

def test_printable_reports_route(auth_client):
    res = auth_client.get('/reports/calving?format=pdf')
    assert res.status_code == 200
    assert 'گزارش زایش‌ها'.encode('utf-8') in res.data
