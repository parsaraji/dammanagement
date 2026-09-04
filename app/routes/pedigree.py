from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.animal import Animal
from app.services.pedigree_service import build_tree_node, calculate_inbreeding_coefficient, calculate_blood_purity

bp = Blueprint('pedigree', __name__)

@bp.route('/animals/<int:id>/pedigree')
@login_required
def show(id):
    animal = Animal.query.get_or_404(id)
    tree = build_tree_node(animal)
    inbreeding = calculate_inbreeding_coefficient(animal)
    purity = calculate_blood_purity(animal)

    return jsonify({
        'tree': tree,
        'inbreeding_coefficient': inbreeding,
        'blood_purity': purity
    })
