def test_homepage(client):
    # test that viewing the page renders without template errors
    assert client.get("/").status_code == 200
