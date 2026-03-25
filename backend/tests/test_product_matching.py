import io


def _create_product(client, auth_headers, payload):
    response = client.post("/api/v1/products/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


def _create_vendor(client, auth_headers, vendor_code: str, vendor_name: str):
    response = client.post(
        "/api/v1/vendors/",
        json={"vendor_code": vendor_code, "vendor_name": vendor_name, "is_active": True},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


def _add_mapping(
    client,
    auth_headers,
    vendor_id: int,
    product_id: int,
    vendor_sku: str,
    vendor_description: str,
    is_primary: bool = True,
    vendor_uom: str | None = None,
):
    response = client.post(
        "/api/v1/mappings/",
        json={
            "vendor_id": vendor_id,
            "product_id": product_id,
            "vendor_sku": vendor_sku,
            "vendor_description": vendor_description,
            "vendor_uom": vendor_uom,
            "is_primary": is_primary,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


def _add_alias(client, auth_headers, internal_sku: str, alias_text: str):
    rows = f"internal_sku,alias_text,alias_type,is_preferred\n{internal_sku},{alias_text},trade,true\n".encode()
    response = client.post(
        "/api/v1/imports/sheet-csv",
        params={"sheet_name": "item_aliases"},
        files={"file": ("item_aliases.csv", io.BytesIO(rows), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_product_match_exact_internal_sku(client, auth_headers):
    _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-EXACT-1", "normalized_name": "Exact Board", "status": "active"},
    )

    response = client.post("/api/v1/products/match", json={"query_text": "sku-exact-1"}, headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["matches"], f"Expected at least one match, got payload={payload}"
    assert payload["matches"][0]["internal_sku"] == "SKU-EXACT-1"
    assert payload["matches"][0]["confidence"] == "high"
    assert "exact internal_sku match" in payload["matches"][0]["match_reasons"]


def test_product_match_exact_vendor_sku(client, auth_headers):
    product = _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-VENDOR-1", "normalized_name": "Vendor Board", "status": "active"},
    )
    vendor = _create_vendor(client, auth_headers, "VEND-A", "Vendor A")
    _add_mapping(client, auth_headers, vendor["id"], product["id"], "VN-001-A", "Vendor A board", vendor_uom="EA")

    response = client.post(
        "/api/v1/products/match",
        json={"vendor_sku": "vn-001-a", "vendor_code": "vend-a"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["matches"], f"Expected at least one match, got payload={payload}"
    top = payload["matches"][0]
    assert top["product_id"] == product["id"]
    assert top["confidence"] == "high"
    assert top["matched_vendor_sku"] == "VN-001-A"
    assert top["matched_vendor_uom"] == "EA"
    assert "exact vendor_sku match" in top["match_reasons"]


def test_product_match_vendor_uom_signal(client, auth_headers):
    product = _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-UOM-1", "normalized_name": "Vendor UOM Product", "status": "active"},
    )
    vendor = _create_vendor(client, auth_headers, "UOM-A", "Unit Vendor")
    _add_mapping(client, auth_headers, vendor["id"], product["id"], "UOM-100", "bundle board", vendor_uom="BUNDLE")

    response = client.post("/api/v1/products/match", json={"query_text": "bundle"}, headers=auth_headers)
    assert response.status_code == 200
    top = response.json()["matches"][0]
    assert top["product_id"] == product["id"]
    assert top["matched_vendor_uom"] == "BUNDLE"


def test_product_match_alias_signal(client, auth_headers):
    product = _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-ALIAS-MATCH", "normalized_name": "Alias Signal Product", "status": "active"},
    )
    _add_alias(client, auth_headers, "SKU-ALIAS-MATCH", "Contractor Legacy Pine")

    response = client.post("/api/v1/products/match", json={"query_text": "contractor legacy pine"}, headers=auth_headers)
    assert response.status_code == 200
    top = response.json()["matches"][0]
    assert top["product_id"] == product["id"]
    assert "exact alias match" in top["match_reasons"]


def test_product_match_search_text_and_display_name(client, auth_headers):
    product = _create_product(
        client,
        auth_headers,
        {
            "internal_sku": "SKU-TEXT-1",
            "normalized_name": "Prime Trim Board",
            "display_name": "Prime Trim",
            "canonical_name": "Prime Trim Board",
            "search_text": "legacy trim smooth line",
            "master_search_text": "beisser premium trim board",
            "status": "active",
        },
    )
    response = client.post("/api/v1/products/match", json={"query_text": "beisser premium trim"}, headers=auth_headers)
    assert response.status_code == 200
    top = response.json()["matches"][0]
    assert top["product_id"] == product["id"]
    assert any("master_search_text" in reason for reason in top["match_reasons"])


def test_product_match_vendor_aware_boosting(client, auth_headers):
    preferred_product = _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-BOOST-A", "normalized_name": "Boost Product A", "status": "active"},
    )
    other_product = _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-BOOST-B", "normalized_name": "Boost Product B", "status": "active"},
    )
    vendor_a = _create_vendor(client, auth_headers, "BOOSTA", "Boost Vendor A")
    vendor_b = _create_vendor(client, auth_headers, "BOOSTB", "Boost Vendor B")
    _add_mapping(client, auth_headers, vendor_a["id"], preferred_product["id"], "SHARED-100", "shared board text")
    _add_mapping(client, auth_headers, vendor_b["id"], other_product["id"], "SHARED-100", "shared board text")

    response = client.post(
        "/api/v1/products/match",
        json={"vendor_sku": "SHARED-100", "vendor_code": "BOOSTA"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    top = response.json()["matches"][0]
    assert top["product_id"] == preferred_product["id"]
    assert top["matched_vendor_code"] == "BOOSTA"
    assert "exact vendor_code match" in top["match_reasons"]


def test_product_match_limit_and_reasons(client, auth_headers):
    for n in range(1, 4):
        _create_product(
            client,
            auth_headers,
            {"internal_sku": f"SKU-LIMIT-{n}", "normalized_name": f"Limit Product {n}", "search_text": "limit token", "status": "active"},
        )
    response = client.post("/api/v1/products/match", json={"query_text": "limit token", "limit": 2}, headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["matches"]) == 2
    assert all(row["match_reasons"] for row in payload["matches"])


def test_product_match_handles_noisy_input_without_crashing(client, auth_headers):
    _create_product(
        client,
        auth_headers,
        {"internal_sku": "SKU-NOISE", "normalized_name": "Noise Product", "status": "active"},
    )
    response = client.post("/api/v1/products/match", json={"query_text": "!!!   ??? ---"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["matches"] == []


def test_product_match_requires_signal(client, auth_headers):
    response = client.post("/api/v1/products/match", json={"query_text": "   "}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid request payload"
