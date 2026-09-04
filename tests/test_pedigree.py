from app.models.animal import Animal
from app.services.pedigree_service import calculate_inbreeding_coefficient

def test_half_sibling_inbreeding_coefficient(app):
    with app.app_context():
        # IR-G2-INB1 is offspring of gen1_dam1 and gen1_sire1 who share mother g0_m1
        inbred_animal = Animal.query.filter_by(plastic_tag='IR-G2-INB1').first()
        assert inbred_animal is not None

        f_val = calculate_inbreeding_coefficient(inbred_animal)
        # Expected Wright's F for half-siblings is (1/2)^3 = 0.125
        assert abs(f_val - 0.125) < 0.01
