from app import create_app

app = create_app()

import os

if __name__ == '__main__':
    debug_flag = os.environ.get('FLASK_DEBUG', '0') in ['1', 'true', 'True']
    app.run(host='0.0.0.0', port=5000, debug=debug_flag)
