from app.models.animal import Animal
from app.services.milk_service import compute_standardized_milk

def test_milk_standardization(app):
    with app.app_context():
        # Well populated female (IR-G1-F2)
        female_well = Animal.query.filter_by(plastic_tag='IR-G1-F2').first()
        res_well = compute_standardized_milk(female_well.id, female_well.parity or 1)
        assert res_well['success'] is True
        assert res_well['avg'] > 0

        # Sparse female (IR-G1-F1)
        female_sparse = Animal.query.filter_by(plastic_tag='IR-G1-F1').first()
        res_sparse = compute_standardized_milk(female_sparse.id, female_sparse.parity or 1)
        assert res_sparse['success'] is False
        assert 'کافی نیست' in res_sparse['message']
