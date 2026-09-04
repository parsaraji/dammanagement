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
