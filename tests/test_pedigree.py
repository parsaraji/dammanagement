from datetime import date
from app.extensions import db
from app.models.animal import Animal, Sex, Species, AnimalStatus, Origin
from app.services.pedigree_service import (
    calculate_inbreeding_coefficient, calculate_blood_purity
)

def test_half_sibling_inbreeding_coefficient(app):
    with app.app_context():
        inbred_animal = Animal.query.filter_by(plastic_tag='IR-G2-INB1').first()
        assert inbred_animal is not None

        f_val = calculate_inbreeding_coefficient(inbred_animal)
        # Expected Wright's F for half-siblings is 0.125
        assert abs(f_val - 0.125) < 0.01

def test_full_sibling_inbreeding_coefficient(app):
    with app.app_context():
        father = Animal(plastic_tag='SIRE-FS', serial_number='SFS01', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2020,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        mother = Animal(plastic_tag='DAM-FS', serial_number='DFS01', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2020,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([father, mother])
        db.session.commit()

        sib1 = Animal(plastic_tag='SIB-1', serial_number='S101', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2021,1,1), father_id=father.id, mother_id=mother.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        sib2 = Animal(plastic_tag='SIB-2', serial_number='S201', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2021,1,1), father_id=father.id, mother_id=mother.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([sib1, sib2])
        db.session.commit()

        # Full sibling mating F = (0.5)^3 + (0.5)^3 = 0.25
        f_val = calculate_inbreeding_coefficient(sib1.id, sib2.id)
        assert abs(f_val - 0.25) < 0.01

def test_parent_offspring_inbreeding_coefficient(app):
    with app.app_context():
        father = Animal(plastic_tag='SIRE-PO', serial_number='SPO01', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2019,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        mother = Animal(plastic_tag='DAM-PO', serial_number='DPO01', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2019,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([father, mother])
        db.session.commit()

        daughter = Animal(plastic_tag='DAUGHTER-PO', serial_number='DGT01', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2021,1,1), father_id=father.id, mother_id=mother.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add(daughter)
        db.session.commit()

        # Parent-offspring mating F = 0.25
        f_val = calculate_inbreeding_coefficient(father.id, daughter.id)
        assert abs(f_val - 0.25) < 0.01

def test_cousin_inbreeding_coefficient(app):
    with app.app_context():
        g0_sire = Animal(plastic_tag='G0-S', serial_number='G0S01', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2018,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        g0_dam = Animal(plastic_tag='G0-D', serial_number='G0D01', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2018,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([g0_sire, g0_dam])
        db.session.commit()

        # Full sib parents
        p1 = Animal(plastic_tag='P1', serial_number='P101', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2019,1,1), father_id=g0_sire.id, mother_id=g0_dam.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        p2 = Animal(plastic_tag='P2', serial_number='P201', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2019,1,1), father_id=g0_sire.id, mother_id=g0_dam.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([p1, p2])
        db.session.commit()

        # Unrelated mates
        m1 = Animal(plastic_tag='M1', serial_number='M101', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2019,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        m2 = Animal(plastic_tag='M2', serial_number='M201', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2019,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([m1, m2])
        db.session.commit()

        # First cousins
        cousin1 = Animal(plastic_tag='C1', serial_number='C101', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2021,1,1), father_id=p1.id, mother_id=m1.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        cousin2 = Animal(plastic_tag='C2', serial_number='C201', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2021,1,1), father_id=m2.id, mother_id=p2.id, status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([cousin1, cousin2])
        db.session.commit()

        # First cousin mating F = 2 * (0.5)^5 = 0.0625
        f_val = calculate_inbreeding_coefficient(cousin1.id, cousin2.id)
        assert abs(f_val - 0.0625) < 0.01

def test_pedigree_cycle_resilience(app):
    with app.app_context():
        a1 = Animal(plastic_tag='A1-CYC', serial_number='A1C', sex=Sex.MALE, species=Species.SHEEP, birth_date=date(2020,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        a2 = Animal(plastic_tag='A2-CYC', serial_number='A2C', sex=Sex.FEMALE, species=Species.SHEEP, birth_date=date(2020,1,1), status=AnimalStatus.ALIVE, origin=Origin.BORN_IN_FARM)
        db.session.add_all([a1, a2])
        db.session.commit()

        # Artificially inject cycle A1 -> A2 -> A1
        a1.father_id = a2.id
        a2.father_id = a1.id
        db.session.commit()

        purity = calculate_blood_purity(a1)
        assert purity == 100.0

        f_val = calculate_inbreeding_coefficient(a1.id, a2.id)
        assert isinstance(f_val, float)
