import pytest as pytest
from fastapi.testclient import TestClient
from main import app  # Ensure this points to where your FastAPI app is defined
from unittest.mock import patch
import pandas as pd
from datetime import datetime

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture


################################### Test Case 1 #############################################
def mock_user_history_data():
    data = {
        "USER_ID": [1, 2],
        "BOOK_ID": [101, 102],
        "flag": [True, False],  # Assuming flag is a boolean
        "rating": [None, None]
    }
    return pd.DataFrame(data)
def test_get_snowflake_recommendation_user_history_success(test_client, mock_user_history_data):
    with patch('path.to.snowflake_connector.get_user_history_data_recommendations') as mock_db_call:
        mock_db_call.return_value = mock_user_history_data
        response = test_client.get("/snowflake_recommendation_user_history")
        expected_json = [
            {"USER_ID": 1, "BOOK_ID": 101, "flag": 0, "rating": None},
            {"USER_ID": 2, "BOOK_ID": 102, "flag": 2, "rating": None}
        ]
        assert response.status_code == 200
        assert "snowflake_recommendation_user_history" in response.json() 
        print(response.status_code)

def test_get_snowflake_recommendation_user_history_failure(test_client):
    with patch('path.to.snowflake_connector.get_user_history_data_recommendations', side_effect=Exception("Database error")):
        response = test_client.get("/snowflake_recommendation_user_history")
        assert response.status_code == 200  # Depending on how you handle errors, this might need to be 500
        assert response.json() == {"error": "Database error"}
        print(response.json)


########################### Test Case 2 ##########################################

@pytest.fixture
def mock_user_recommendation_data():
    import pandas as pd
    data = {
        "book_id": ["123,345,645", "456,342", "789"]
    }
    df = pd.DataFrame(data)
    return df

@patch('your_module.get_user_recommendation_data')
def test_get_snowflake_user_recommendation(mock_get_recommendation, test_client, mock_user_recommendation_data):
    mock_get_recommendation.return_value = mock_user_recommendation_data
    user_id = 1
    response = test_client.get(f"/snowflake_user_recommendation/{user_id}")
    assert response.status_code == 200
    assert response.json() == [
        {"book_id": "123"},
        {"book_id": "456"},
        {"book_id": "789"}
    ]

@patch('your_module.get_user_recommendation_data', side_effect=Exception("Database error"))
def test_get_snowflake_user_recommendation_error(mock_get_recommendation, test_client):
    user_id = 1
    response = test_client.get(f"/snowflake_user_recommendation/{user_id}")
    assert response.status_code == 200  # Or 500 if your error handling changes the status code
    assert response.json() == {"error": "Database error"}
