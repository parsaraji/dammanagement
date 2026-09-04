def test_login_success(client):
    res = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert res.status_code == 200
    assert 'داشبورد' in res.get_data(as_text=True)

def test_login_failure(client):
    res = client.post('/login', data={'username': 'admin', 'password': 'wrongpassword'}, follow_redirects=True)
    assert res.status_code == 200
    assert 'نام کاربری یا رمز عبور اشتباه است' in res.get_data(as_text=True)

def test_admin_route_blocked_for_non_admin(client):
    # Login as operator
    client.post('/login', data={'username': 'operator1', 'password': 'operator1123'}, follow_redirects=True)
    res = client.get('/admin/users', follow_redirects=True)
    assert 'دستور' in res.get_data(as_text=True) or 'دسترسی لازم' in res.get_data(as_text=True)

def test_csrf_header_protection(client, app):
    # Test CSRF header validation on AJAX POST
    app.config['WTF_CSRF_ENABLED'] = True
    with client:
        client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        # Request without CSRF token should return 400
        res = client.post('/bulk-operations/select', data={'species': 'sheep'})
        assert res.status_code == 400

        # Request with X-CSRFToken header or form token should pass validation
        token_res = client.get('/bulk-operations')
        import re
        match = re.search(r'name="csrf-token" content="([^"]+)"', token_res.get_data(as_text=True))
        if match:
            csrf_token = match.group(1)
            valid_res = client.post('/bulk-operations/select', data={'species': 'sheep'}, headers={'X-CSRFToken': csrf_token}, follow_redirects=True)
            assert valid_res.status_code == 200
    app.config['WTF_CSRF_ENABLED'] = False
