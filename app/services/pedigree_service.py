from app.extensions import db
from app.models.animal import Animal

def get_ancestors_with_paths(animal_id, max_depth=6, current_depth=0, visited=None):
    """
    Returns dict mapping ancestor_id -> list of path depths from specified animal.
    Prevents infinite cycles via visited set.
    """
    if visited is None:
        visited = set()

    if not animal_id or current_depth >= max_depth or animal_id in visited:
        return {}

    visited.add(animal_id)
    animal = db.session.get(Animal, animal_id)
    if not animal:
        visited.remove(animal_id)
        return {}

    ancestors = {}
    sire_id = animal.father_id
    dam_id = animal.mother_id

    for parent_id in [sire_id, dam_id]:
        if parent_id:
            if parent_id not in ancestors:
                ancestors[parent_id] = []
            ancestors[parent_id].append(current_depth + 1)

            sub_ancestors = get_ancestors_with_paths(parent_id, max_depth, current_depth + 1, set(visited))
            for anc_id, depths in sub_ancestors.items():
                if anc_id not in ancestors:
                    ancestors[anc_id] = []
                ancestors[anc_id].extend(depths)

    visited.remove(animal_id)
    return ancestors

def calculate_inbreeding_coefficient(sire_id_or_animal1, dam_id_or_animal2=None, max_depth=6):
    """
    Calculates Wright's inbreeding coefficient F using recursive ancestor evaluation.
    Handles ancestor inbreeding F_A.
    """
    if dam_id_or_animal2 is None:
        animal = sire_id_or_animal1 if isinstance(sire_id_or_animal1, Animal) else db.session.get(Animal, sire_id_or_animal1)
        if not animal or not animal.father_id or not animal.mother_id:
            return 0.0
        sire_id = animal.father_id
        dam_id = animal.mother_id
    else:
        sire_id = sire_id_or_animal1.id if isinstance(sire_id_or_animal1, Animal) else sire_id_or_animal1
        dam_id = dam_id_or_animal2.id if isinstance(dam_id_or_animal2, Animal) else dam_id_or_animal2

    if not sire_id or not dam_id:
        return 0.0

    if sire_id == dam_id:
        return 0.5

    sire_ancestors = get_ancestors_with_paths(sire_id, max_depth=max_depth)
    dam_ancestors = get_ancestors_with_paths(dam_id, max_depth=max_depth)

    # Self as depth 0 ancestor
    sire_ancestors[sire_id] = [0] + sire_ancestors.get(sire_id, [])
    dam_ancestors[dam_id] = [0] + dam_ancestors.get(dam_id, [])

    common_ancestors = set(sire_ancestors.keys()).intersection(set(dam_ancestors.keys()))
    if not common_ancestors:
        return 0.0

    total_f = 0.0
    for anc_id in common_ancestors:
        # Calculate ancestor's own inbreeding coefficient F_A if ancestor has parents
        f_a = 0.0
        anc_obj = db.session.get(Animal, anc_id)
        if anc_obj and anc_obj.father_id and anc_obj.mother_id and max_depth > 2:
            f_a = calculate_inbreeding_coefficient(anc_obj.father_id, anc_obj.mother_id, max_depth=max_depth-2)

        for d_s in sire_ancestors[anc_id]:
            for d_d in dam_ancestors[anc_id]:
                total_f += (0.5 ** (d_s + d_d + 1)) * (1.0 + f_a)

    return round(total_f, 4)

def calculate_blood_purity(animal, visited=None):
    """Calculates estimated blood purity percentage safely against cycles and missing data."""
    if visited is None:
        visited = set()

    if not animal or animal.id in visited:
        return 100.0

    visited.add(animal.id)

    if not animal.mother_id and not animal.father_id:
        return 100.0

    mother_purity = calculate_blood_purity(animal.mother, set(visited)) if animal.mother else 100.0
    father_purity = calculate_blood_purity(animal.father, set(visited)) if animal.father else 100.0

    return round((mother_purity + father_purity) / 2.0, 2)

def build_tree_node(animal, current_gen=0, max_gen=4):
    """Builds a nested dictionary representation of animal's pedigree tree up to max_gen."""
    if not animal or current_gen >= max_gen:
        return None

    sire_obj = animal.father
    dam_obj = animal.mother

    return {
        'id': animal.id,
        'tag': animal.plastic_tag,
        'serial': animal.serial_number,
        'sex': animal.sex.value if hasattr(animal.sex, 'value') else animal.sex,
        'breed': animal.breed,
        'species': animal.species.value if hasattr(animal.species, 'value') else animal.species,
        'father': build_tree_node(sire_obj, current_gen + 1, max_gen),
        'mother': build_tree_node(dam_obj, current_gen + 1, max_gen)
    }
