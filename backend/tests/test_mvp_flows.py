import io


def test_health_endpoint(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_auth_login_success(client):
    response = client.post('/api/v1/auth/login', json={'email': 'admin@test.com', 'password': 'Password123!'})
    assert response.status_code == 200
    assert response.json()['access_token']


def test_auth_login_failure(client):
    response = client.post('/api/v1/auth/login', json={'email': 'admin@test.com', 'password': 'wrong-password'})
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


def test_product_search_matches_enriched_fields(client, auth_headers):
    client.post(
        '/api/v1/products/',
        json={
            'internal_sku': 'SKU-SEARCH-1',
            'normalized_name': 'Utility Board',
            'description': 'Core product',
            'canonical_name': 'Prime White Oak Board',
            'display_name': 'White Oak Premium',
            'keywords': 'durable,millwork,finish',
            'search_text': 'legacy code yellow tag',
            'master_search_text': 'beisser showroom premium plank',
            'status': 'active',
        },
        headers=auth_headers,
    )

    expectations = [
        ('prime white', 'SKU-SEARCH-1'),
        ('oak premium', 'SKU-SEARCH-1'),
        ('millwork', 'SKU-SEARCH-1'),
        ('yellow tag', 'SKU-SEARCH-1'),
        ('showroom premium', 'SKU-SEARCH-1'),
    ]
    for term, expected_sku in expectations:
        response = client.get('/api/v1/products/', params={'search': term}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()['meta']['total'] == 1
        assert response.json()['items'][0]['internal_sku'] == expected_sku


def test_product_search_matches_alias_without_duplicate_rows(client, auth_headers):
    product_1 = client.post('/api/v1/products/', json={'internal_sku': 'SKU-ALIAS-1', 'normalized_name': 'Alias Product 1', 'status': 'active'}, headers=auth_headers).json()
    client.post('/api/v1/products/', json={'internal_sku': 'SKU-ALIAS-2', 'normalized_name': 'Alias Product 2', 'status': 'active'}, headers=auth_headers)

    alias_rows = (
        b'internal_sku,alias_text,alias_type,is_preferred\n'
        b'SKU-ALIAS-1,Contractor Pine,trade,true\n'
        b'SKU-ALIAS-1,Contractor Pine Board,trade,false\n'
    )
    import_res = client.post(
        '/api/v1/imports/sheet-csv',
        params={'sheet_name': 'item_aliases'},
        files={'file': ('item_aliases.csv', io.BytesIO(alias_rows), 'text/csv')},
        headers=auth_headers,
    )
    assert import_res.status_code == 200

    response = client.get('/api/v1/products/', params={'search': 'contractor pine'}, headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['meta']['total'] == 1
    assert len(payload['items']) == 1
    assert payload['items'][0]['id'] == product_1['id']
    assert payload['items'][0]['internal_sku'] == 'SKU-ALIAS-1'


def test_product_search_pagination_and_filters_work_together(client, auth_headers):
    v1 = client.post('/api/v1/vendors/', json={'vendor_code': 'VS1', 'vendor_name': 'Vendor Search 1', 'is_active': True}, headers=auth_headers).json()
    v2 = client.post('/api/v1/vendors/', json={'vendor_code': 'VS2', 'vendor_name': 'Vendor Search 2', 'is_active': True}, headers=auth_headers).json()

    p1 = client.post(
        '/api/v1/products/',
        json={'internal_sku': 'SKU-PAGE-1', 'normalized_name': 'Page Product 1', 'master_search_text': 'focus-term', 'status': 'active', 'category_major': 'Lumber'},
        headers=auth_headers,
    ).json()
    p2 = client.post(
        '/api/v1/products/',
        json={'internal_sku': 'SKU-PAGE-2', 'normalized_name': 'Page Product 2', 'master_search_text': 'focus-term', 'status': 'active', 'category_major': 'Lumber'},
        headers=auth_headers,
    ).json()
    client.post(
        '/api/v1/products/',
        json={'internal_sku': 'SKU-PAGE-3', 'normalized_name': 'Page Product 3', 'master_search_text': 'focus-term', 'status': 'inactive', 'category_major': 'Lumber'},
        headers=auth_headers,
    )

    client.post('/api/v1/mappings/', json={'vendor_id': v1['id'], 'product_id': p1['id'], 'vendor_sku': 'V1-1', 'is_primary': True}, headers=auth_headers)
    client.post('/api/v1/mappings/', json={'vendor_id': v1['id'], 'product_id': p2['id'], 'vendor_sku': 'V1-2', 'is_primary': True}, headers=auth_headers)
    client.post('/api/v1/mappings/', json={'vendor_id': v2['id'], 'product_id': p2['id'], 'vendor_sku': 'V2-2', 'is_primary': True}, headers=auth_headers)

    page_1 = client.get(
        '/api/v1/products/',
        params={
            'search': ' focus-term ',
            'status': 'active',
            'category_major': 'Lumber',
            'vendor_id': v1['id'],
            'page': 1,
            'page_size': 1,
            'sort_by': 'internal_sku',
            'sort_dir': 'asc',
        },
        headers=auth_headers,
    )
    assert page_1.status_code == 200
    body_1 = page_1.json()
    assert body_1['meta']['total'] == 2
    assert len(body_1['items']) == 1
    assert body_1['items'][0]['internal_sku'] == 'SKU-PAGE-1'

    page_2 = client.get(
        '/api/v1/products/',
        params={
            'search': ' focus-term ',
            'status': 'active',
            'category_major': 'Lumber',
            'vendor_id': v1['id'],
            'page': 2,
            'page_size': 1,
            'sort_by': 'internal_sku',
            'sort_dir': 'asc',
        },
        headers=auth_headers,
    )
    assert page_2.status_code == 200
    body_2 = page_2.json()
    assert body_2['meta']['total'] == 2
    assert len(body_2['items']) == 1
    assert body_2['items'][0]['internal_sku'] == 'SKU-PAGE-2'


def test_blank_search_input_does_not_filter(client, auth_headers):
    client.post('/api/v1/products/', json={'internal_sku': 'SKU-BLANK-1', 'normalized_name': 'Blank One', 'status': 'active'}, headers=auth_headers)
    client.post('/api/v1/products/', json={'internal_sku': 'SKU-BLANK-2', 'normalized_name': 'Blank Two', 'status': 'active'}, headers=auth_headers)

    response = client.get('/api/v1/products/', params={'search': '   '}, headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload['meta']['total'] == 2
    assert {item['internal_sku'] for item in payload['items']} == {'SKU-BLANK-1', 'SKU-BLANK-2'}


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


def test_product_detail_includes_enrichment_collections(client, auth_headers):
    product = client.post('/api/v1/products/', json={'internal_sku': 'SKU-DET', 'normalized_name': 'Detail Product', 'status': 'active'}, headers=auth_headers).json()
    res = client.get(f"/api/v1/products/{product['id']}", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert 'aliases' in body
    assert 'images' in body
    assert 'documents' in body


def test_products_seed_import_can_create_note_and_mapping(client, auth_headers):
    csv_content = b'internal_sku,normalized_name,status,note_text,note_type,vendor_code,vendor_sku,vendor_name\nSKU-RICH,Rich Product,active,Seeded note,seed,VN1,VSKU-1,Vendor One\n'
    files = {'file': ('products_seed.csv', io.BytesIO(csv_content), 'text/csv')}
    res = client.post('/api/v1/imports/products-csv', files=files, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()['inserted'] == 1

    product = client.get('/api/v1/products/', params={'search': 'SKU-RICH'}, headers=auth_headers).json()['items'][0]
    detail = client.get(f"/api/v1/products/{product['id']}", headers=auth_headers).json()
    assert len(detail['notes']) == 1
    assert detail['notes'][0]['note_text'] == 'Seeded note'
    assert len(detail['mappings']) == 1
    assert detail['mappings'][0]['vendor_sku'] == 'VSKU-1'


def test_sheet_csv_import_alias_image_document(client, auth_headers):
    product_csv = b'internal_sku,normalized_name,status\nSKU-SHEETS,Sheets Product,active\n'
    client.post('/api/v1/imports/products-csv', files={'file': ('products.csv', io.BytesIO(product_csv), 'text/csv')}, headers=auth_headers)

    aliases = b'internal_sku,alias_text,alias_type,is_preferred\nSKU-SHEETS,Contractor Name,slang,true\n'
    images = b'internal_sku,storage_path,image_type\nSKU-SHEETS,https://example.com/a.jpg,hero\n'
    documents = b'internal_sku,document_type,title,file_url\nSKU-SHEETS,spec_sheet,Spec Sheet,https://example.com/spec.pdf\n'

    a_res = client.post('/api/v1/imports/sheet-csv', params={'sheet_name': 'item_aliases'}, files={'file': ('item_aliases.csv', io.BytesIO(aliases), 'text/csv')}, headers=auth_headers)
    i_res = client.post('/api/v1/imports/sheet-csv', params={'sheet_name': 'item_images'}, files={'file': ('item_images.csv', io.BytesIO(images), 'text/csv')}, headers=auth_headers)
    d_res = client.post('/api/v1/imports/sheet-csv', params={'sheet_name': 'item_documents'}, files={'file': ('item_documents.csv', io.BytesIO(documents), 'text/csv')}, headers=auth_headers)

    assert a_res.status_code == 200
    assert i_res.status_code == 200
    assert d_res.status_code == 200

    product = client.get('/api/v1/products/', params={'search': 'SKU-SHEETS'}, headers=auth_headers).json()['items'][0]
    detail = client.get(f"/api/v1/products/{product['id']}", headers=auth_headers).json()
    assert len(detail['aliases']) == 1
    assert len(detail['images']) == 1
    assert len(detail['documents']) == 1
