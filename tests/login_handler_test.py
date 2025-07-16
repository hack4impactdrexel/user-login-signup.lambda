import pytest
from unittest.mock import patch, MagicMock
from src.main import login_handler, client
import botocore.exceptions

valid_body = {
	"email": "temp@h4i.com",
	"password": "H4i12345$"
}