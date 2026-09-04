from app.models.animal import Animal

def get_ancestors_with_depth(animal_id, max_depth=6, current_depth=0):
    """
    Returns a dict mapping ancestor_id -> list of paths from animal to ancestor.
    A path is a tuple of (depth, parent_type) e.g., (1, 'father'), (2, 'mother').
    """
    if not animal_id or current_depth >= max_depth:
        return {}

    animal = Animal.query.get(animal_id)
    if not animal:
        return {}

    ancestors = {}

    # Get father (either direct animal or via father_sperm)
    sire_id = animal.father_id
    dam_id = animal.mother_id

    for parent_id, p_type in [(sire_id, 'sire'), (dam_id, 'dam')]:
        if parent_id:
            if parent_id not in ancestors:
                ancestors[parent_id] = []
            ancestors[parent_id].append((current_depth + 1, p_type))

            # Recurse
            sub_ancestors = get_ancestors_with_depth(parent_id, max_depth, current_depth + 1)
            for anc_id, paths in sub_ancestors.items():
                if anc_id not in ancestors:
                    ancestors[anc_id] = []
                ancestors[anc_id].extend(paths)

    return ancestors

def calculate_inbreeding_coefficient(sire_id_or_animal1, dam_id_or_animal2=None):
    """
    Calculates Wright's inbreeding coefficient F.
    If animal2 is provided, calculates F for hypothetical offspring of (animal1, animal2).
    If animal2 is None, calculates F for animal1 based on its parents.
    """
    if dam_id_or_animal2 is None:
        animal = sire_id_or_animal1 if isinstance(sire_id_or_animal1, Animal) else Animal.query.get(sire_id_or_animal1)
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
        # Selfing / identical parent
        return 0.5

    sire_ancestors = get_ancestors_with_depth(sire_id, max_depth=6)
    dam_ancestors = get_ancestors_with_depth(dam_id, max_depth=6)

    # Add self to ancestors map at depth 0
    sire_ancestors[sire_id] = [(0, 'self')] + sire_ancestors.get(sire_id, [])
    dam_ancestors[dam_id] = [(0, 'self')] + dam_ancestors.get(dam_id, [])

    common_ancestors = set(sire_ancestors.keys()).intersection(set(dam_ancestors.keys()))

    if not common_ancestors:
        return 0.0

    total_f = 0.0
    for anc_id in common_ancestors:
        # Calculate F_A for ancestor A recursively (to depth 3 to avoid infinite recursion)
        f_a = 0.0 # Default for founders or simple depth

        for d_s, _ in sire_ancestors[anc_id]:
            for d_d, _ in dam_ancestors[anc_id]:
                # n1 = d_s, n2 = d_d
                total_f += (0.5 ** (d_s + d_d + 1)) * (1.0 + f_a)

    return round(total_f, 4)

def calculate_blood_purity(animal):
    """Calculates estimated blood purity percentage based on known purebred ancestors."""
    if not animal:
        return 100.0
    if not animal.mother_id and not animal.father_id:
        return 100.0 # Assumed pure founder if no recorded parents

    mother_purity = calculate_blood_purity(animal.mother) if animal.mother else 100.0
    father_purity = calculate_blood_purity(animal.father) if animal.father else 100.0

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
