import os
from flask import Flask, render_template
from config import Config
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance and upload directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # User loader
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Jinja context processors and filters
    from app.services.jalali import to_jalali
    @app.template_filter('jalali')
    def jalali_filter(value, fmt='%Y/%m/%d'):
        return to_jalali(value, fmt)

    # Register Blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.animals import bp as animals_bp
    app.register_blueprint(animals_bp)

    from app.routes.pedigree import bp as pedigree_bp
    app.register_blueprint(pedigree_bp)

    from app.routes.medical import bp as medical_bp
    app.register_blueprint(medical_bp)

    from app.routes.reproduction import bp as reproduction_bp
    app.register_blueprint(reproduction_bp)

    from app.routes.other_operations import bp as other_ops_bp
    app.register_blueprint(other_ops_bp)

    from app.routes.milk import bp as milk_bp
    app.register_blueprint(milk_bp)

    from app.routes.bulk_operations import bp as bulk_ops_bp
    app.register_blueprint(bulk_ops_bp)

    from app.routes.records import bp as records_bp
    app.register_blueprint(records_bp)

    from app.routes.pens import bp as pens_bp
    app.register_blueprint(pens_bp)

    from app.routes.herd_composition import bp as herd_comp_bp
    app.register_blueprint(herd_comp_bp)

    from app.routes.sperm_bank import bp as sperm_bank_bp
    app.register_blueprint(sperm_bank_bp)

    from app.routes.medicine_warehouse import bp as medicine_warehouse_bp
    app.register_blueprint(medicine_warehouse_bp)

    from app.routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp)

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # Auto-create tables and seed data if DB empty
    with app.app_context():
        db.create_all()
        from app.models.animal import Animal
        try:
            if Animal.query.count() == 0:
                print("Database is empty or missing data. Running seed_demo.seed()...")
                from seed_demo import seed
                seed()
        except Exception as e:
            print(f"Auto-seed check note: {e}")

    return app
