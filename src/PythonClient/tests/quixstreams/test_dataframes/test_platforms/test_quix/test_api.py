from src.quixstreams.dataframes.platforms.quix.api import QuixPortalApiService
from io import BytesIO
import zipfile
from unittest.mock import create_autospec


class TestApi:
    def test_get_workspace_certificate(self):
        zip_in_mem = BytesIO()
        with zipfile.ZipFile(zip_in_mem, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("ca.cert", BytesIO(b"my cool cert stuff").getvalue())

        ws = '12345'
        api = QuixPortalApiService(portal_api='http://portal.com', auth_token='token')
        api.session = create_autospec(QuixPortalApiService.SessionWithUrlBase)
        api.session.get(f"/workspaces/{ws}/certificates").content = zip_in_mem.getvalue()

        result = api.get_workspace_certificate(ws)
        assert result == b"my cool cert stuff"