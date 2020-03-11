from django.urls import reverse


def test_api(client, mocker):
    yaml = """
    cluster_id: bar
    bad_data: boo
    """
    mocker.patch('builtins.open', mocker.mock_open(read_data=yaml))
    response = client.get(reverse('api:index'))
    assert response.json() == {"cluster_id": "bar"}
