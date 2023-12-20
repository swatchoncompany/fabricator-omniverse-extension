import requests
import math

class FabricatorService:
    ASSETS_URL = 'https://gateway.vmod.com/library/texture_generations/omniverse/list'

    def set_access_token(self, access_token):
        self.access_token = access_token

    def load_assets(self, workspace_id, page, limit):
        headers = { 'Authorization': f'Bearer {self.access_token}', 'current-workspace-id': workspace_id }
        if page < 1:
            page = 1
        offset = (page - 1) * limit

        try:
            response = requests.get(f'{FabricatorService.ASSETS_URL}?offset={offset}&limit={limit}', headers = headers)
            response.raise_for_status()

            body = response.json()
            count = max(math.ceil(body['count'] / limit), 1)
            return [list(map(lambda d: { 'id': d['id'], 'code': d['code'], 'asset_url': d['usdaUrl'], 'thumbnail_url': d['thumbnail']['blackSmallUrl']}, body['data'])), count]
        except:
            raise Exception('Invalid credentials')