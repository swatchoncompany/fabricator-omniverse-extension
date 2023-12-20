from pathlib import Path
import json
import math

class MockFabricatorService:
    mock_data_path = Path(__file__).parent / 'mock.json'
    mock2_data_path = Path(__file__).parent / 'mock2.json'

    def __init__(self):
        self.data = []
        self.data2 = []

        with open(MockFabricatorService.mock_data_path, 'r') as file:
            self.data = json.load(file)
        
        with open(MockFabricatorService.mock2_data_path, 'r') as file:
            self.data2 = json.load(file)

    def set_access_token(self, access_token):
        self.access_token = access_token

    def load_assets(self, workspace_id, page, limit):
        data = self.data if (workspace_id == 1) else self.data2

        assets = data[((page - 1) * limit):(page * limit)]
        count = math.ceil(len(data) / limit)

        return [assets, count]
