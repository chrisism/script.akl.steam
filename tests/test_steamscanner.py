import unittest, os
import unittest.mock
from unittest.mock import MagicMock, patch

import json
import logging

from tests.fakes import FakeProgressDialog, random_string, FakeFile

logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG)
logger = logging.getLogger(__name__)

from resources.lib.scanner import SteamScanner

from akl.api import ROMObj

def read_file(path):
    with open(path, 'r') as f:
        return f.read()
    
class Test_SteamScanner(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
    
    @patch('akl.api.client_get_roms_in_collection')
    @patch('akl.api.client_get_source_scanner_settings')
    @patch('resources.lib.scanner.net.get_URL') 
    def test_when_scanning_your_steam_account_not_existing_dead_roms_will_be_correctly_removed(self, 
            mock_urlopen:MagicMock, api_settings_mock:MagicMock, api_roms_mock:MagicMock):
        # arrange
        source_id = random_string(5)
        mock_urlopen.return_value = json.loads(read_file(self.TEST_ASSETS_DIR + "/steamresponse.json")), 200

        api_settings_mock.return_value = {
            'steam-api-key': 'ABC123', #'BA1B6D6926F84920F8035F95B9B3E824'
            'steamid': '09090909' #'76561198405030123' 
        }               
        
        roms = []
        roms.append(ROMObj({'id': '1', 'scanned_by_id': source_id, 'm_name': 'this-one-will-be-deleted', 'steamid': 99999}))
        roms.append(ROMObj({'id': '2', 'scanned_by_id': source_id, 'm_name': 'this-one-will-be-deleted-too', 'steamid': 777888444}))
        roms.append(ROMObj({'id': '3', 'scanned_by_id': source_id, 'm_name': 'Rocket League', 'steamid': 252950}))
        roms.append(ROMObj({'id': '4', 'scanned_by_id': source_id, 'm_name': 'this-one-will-be-deleted-again', 'steamid': 663434}))             
        api_roms_mock.return_value = roms

        report_dir = FakeFile('//fake_reports/')
        expected = 5

        # act
        target = SteamScanner(report_dir, source_id, None, 0, FakeProgressDialog())
        target.scan()
        
        actual = target.amount_of_scanned_roms()

        # assert
        self.assertIsNotNone(target.scanned_roms)
        assert actual == expected

if __name__ == '__main__':    
    unittest.main()
