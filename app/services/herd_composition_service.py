from datetime import date
from app.models.animal import Animal, AnimalStatus, Sex
from app.models.reproduction import Insemination, Calving, DryOff

def calculate_herd_composition(as_of_date: date) -> dict:
    """
    Genuinely aggregates herd composition counts from live Animal and Reproduction records
    as of specified date.
    """
    if not as_of_date:
        as_of_date = date.today()

    # Alive animals as of date
    alive_query = Animal.query.filter(
        Animal.created_at <= as_of_date,
        (Animal.status.in_([AnimalStatus.ALIVE, AnimalStatus.READY_FOR_REMOVAL])) |
        ((Animal.status == AnimalStatus.REMOVED) & (Animal.removal_date > as_of_date))
    )

    alive_animals = alive_query.all()
    total_count = len(alive_animals)

    male_count = sum(1 for a in alive_animals if a.sex == Sex.MALE)
    female_count = sum(1 for a in alive_animals if a.sex == Sex.FEMALE)

    # Lambs: age <= 180 days (6 months) as of date
    lamb_count = 0
    for a in alive_animals:
        if a.birth_date:
            age_days = (as_of_date - a.birth_date).days
            if 0 <= age_days <= 180:
                lamb_count += 1

    # Pregnant females: last insemination led to pregnancy with no subsequent calving or dry-off
    pregnant_count = 0
    lactating_count = 0
    dry_count = 0

    females = [a for a in alive_animals if a.sex == Sex.FEMALE]
    for f in females:
        # Check active dry off
        open_dry = DryOff.query.filter(
            DryOff.animal_id == f.id,
            DryOff.start_date <= as_of_date,
            (DryOff.end_date.is_(None) | (DryOff.end_date >= as_of_date))
        ).first()

        if open_dry:
            dry_count += 1

        # Check last insemination before date
        last_insem = f.inseminations.filter(Insemination.date <= as_of_date).order_by(Insemination.date.desc()).first()
        last_calving = f.calvings.filter(Calving.date <= as_of_date).order_by(Calving.date.desc()).first()

        if last_insem and last_insem.led_to_pregnancy:
            if not last_calving or last_calving.date < last_insem.date:
                pregnant_count += 1

        # Check lactating: has a calving and no subsequent open dry off
        if last_calving and not open_dry:
            lactating_count += 1

    return {
        'date': as_of_date,
        'male_count': male_count,
        'female_count': female_count,
        'lamb_count': lamb_count,
        'pregnant_count': pregnant_count,
        'lactating_count': lactating_count,
        'dry_count': dry_count,
        'total_count': total_count
    }
