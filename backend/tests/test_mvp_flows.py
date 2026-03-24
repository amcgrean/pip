import io


def test_health_endpoint(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_auth_login_success(client):
    response = client.post('/api/v1/auth/login', json={'email': 'admin@test.local', 'password': 'Password123!'})
    assert response.status_code == 200
    assert response.json()['access_token']


def test_auth_login_failure(client):
    response = client.post('/api/v1/auth/login', json={'email': 'admin@test.local', 'password': 'wrong-password'})
    assert response.status_code == 401


def test_protected_route_requires_auth(client):
    response = client.get('/api/v1/products/')
    assert response.status_code == 401


def test_product_crud(client, auth_headers):
    create = client.post('/api/v1/products/', json={'internal_sku': 'SKU-1', 'normalized_name': 'Test Product', 'status': 'active'}, headers=auth_headers)
    assert create.status_code == 201
    product_id = create.json()['id']

    update = client.put(f'/api/v1/products/{product_id}', json={'normalized_name': 'Updated Product'}, headers=auth_headers)
    assert update.status_code == 200
    assert update.json()['normalized_name'] == 'Updated Product'

    listing = client.get('/api/v1/products/', headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()['meta']['total'] == 1


def test_product_filter_behavior(client, auth_headers):
    client.post('/api/v1/products/', json={'internal_sku': 'SKU-10', 'normalized_name': 'Oak Board', 'status': 'active'}, headers=auth_headers)
    client.post('/api/v1/products/', json={'internal_sku': 'SKU-11', 'normalized_name': 'Pine Board', 'status': 'inactive'}, headers=auth_headers)
    response = client.get('/api/v1/products/', params={'search': 'oak', 'status': 'active'}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['meta']['total'] == 1
    assert response.json()['items'][0]['internal_sku'] == 'SKU-10'


def test_vendor_mapping_creation(client, auth_headers):
    vendor = client.post('/api/v1/vendors/', json={'vendor_code': 'ABC', 'vendor_name': 'Vendor A', 'is_active': True}, headers=auth_headers).json()
    product = client.post('/api/v1/products/', json={'internal_sku': 'SKU-2', 'normalized_name': 'Map Product', 'status': 'active'}, headers=auth_headers).json()
    mapping = client.post('/api/v1/mappings/', json={'vendor_id': vendor['id'], 'product_id': product['id'], 'vendor_sku': 'V-123', 'is_primary': True}, headers=auth_headers)
    assert mapping.status_code == 201
    assert mapping.json()['vendor_sku'] == 'V-123'


def test_vendor_mapping_single_primary_behavior(client, auth_headers):
    vendor = client.post('/api/v1/vendors/', json={'vendor_code': 'MAP1', 'vendor_name': 'Vendor Map', 'is_active': True}, headers=auth_headers).json()
    product = client.post('/api/v1/products/', json={'internal_sku': 'SKU-MAP', 'normalized_name': 'Map Product', 'status': 'active'}, headers=auth_headers).json()
    first = client.post('/api/v1/mappings/', json={'vendor_id': vendor['id'], 'product_id': product['id'], 'vendor_sku': 'ONE', 'is_primary': True}, headers=auth_headers).json()
    second = client.post('/api/v1/mappings/', json={'vendor_id': vendor['id'], 'product_id': product['id'], 'vendor_sku': 'TWO', 'is_primary': True}, headers=auth_headers).json()
    assert first['is_primary'] is True
    assert second['is_primary'] is True

    rows = client.get(f"/api/v1/mappings/product/{product['id']}", headers=auth_headers).json()
    primary_count = len([row for row in rows if row['is_primary'] is True])
    assert primary_count == 1
    assert rows[0]['vendor_sku'] == 'TWO'


def test_import_upsert_behavior(client, auth_headers):
    csv_content = b'internal_sku,normalized_name,vendor_code,vendor_sku,status\nSKU-3,Import Product,VEND1,VSKU1,active\nSKU-3,Import Product Updated,VEND1,VSKU1,active\n'
    files = {'file': ('products.csv', io.BytesIO(csv_content), 'text/csv')}
    res = client.post('/api/v1/imports/products-csv', files=files, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()['total_rows'] == 2
    assert res.json()['inserted'] == 1
    assert res.json()['updated'] == 1


def test_import_missing_required_columns(client, auth_headers):
    csv_content = b'internal_sku,normalized_name,vendor_code\nSKU-3,Import Product,VEND1\n'
    files = {'file': ('products.csv', io.BytesIO(csv_content), 'text/csv')}
    res = client.post('/api/v1/imports/products-csv', files=files, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()['status'] == 'failed'

    jobs = client.get('/api/v1/imports/jobs', headers=auth_headers).json()['items']
    assert 'Missing required columns' in jobs[0]['error_log']


def test_import_blank_rows_are_ignored(client, auth_headers):
    csv_content = b'internal_sku,normalized_name,vendor_code,vendor_sku,status\n\nSKU-4,Import Product,VEND1,VSKU1,active\n'
    files = {'file': ('products.csv', io.BytesIO(csv_content), 'text/csv')}
    res = client.post('/api/v1/imports/products-csv', files=files, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()['total_rows'] == 1


def test_attachment_metadata_creation(client, auth_headers):
    product = client.post('/api/v1/products/', json={'internal_sku': 'SKU-ATT', 'normalized_name': 'Attach Product', 'status': 'active'}, headers=auth_headers).json()
    files = {'file': ('note.txt', io.BytesIO(b'hello'), 'text/plain')}
    upload = client.post(f'/api/v1/attachments/product/{product["id"]}', files=files, headers=auth_headers)
    assert upload.status_code == 201
    attachments = client.get(f'/api/v1/attachments/product/{product["id"]}', headers=auth_headers)
    assert attachments.status_code == 200
    assert len(attachments.json()) == 1


def test_attachment_upload_validation(client, auth_headers):
    product = client.post('/api/v1/products/', json={'internal_sku': 'SKU-ATT2', 'normalized_name': 'Attach Product 2', 'status': 'active'}, headers=auth_headers).json()
    files = {'file': ('archive.exe', io.BytesIO(b'fake'), 'application/octet-stream')}
    upload = client.post(f'/api/v1/attachments/product/{product["id"]}', files=files, headers=auth_headers)
    assert upload.status_code == 400
