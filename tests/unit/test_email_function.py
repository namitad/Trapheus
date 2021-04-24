import os
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
from emailalert import email_function

os.environ["Region"] = "us-west-2"
os.environ["RecipientEmail"] = "abc@example.com"
os.environ["SenderEmail"] = "xyz@example.com"

@patch("emailalert.email_function.boto3.client")
class TestResourceProvider(unittest.TestCase):

    def setUp(self):
        self.event = {"Error": "RestoreError","Cause": "DBInstanceIdentifier:database-1 ThrottlingError: Rate exceeded"}
        self.mock_email_response = {"MessageId": "Email sent successfully"}

    def test_email_success1(self, mock_client):
        mock_ses = mock_client.return_value
        mock_ses.send_email.return_value = self.mock_email_response
        data = email_function.lambda_handler(self.event, {})
        self.assertEqual(data["Error"], "RestoreError")
        self.assertEqual(data["Cause"], "DBInstanceIdentifier:database-1 ThrottlingError: Rate exceeded")
        self.assertEqual(data["message"], self.mock_email_response["MessageId"])

    def test_email_success2(self, mock_client):
        mock_ses = mock_client.return_value
        mock_ses.send_email.return_value = self.mock_email_response
        event = {"taskname": "Restore","status": "inaccessible-encryption-credentials"}
        data = email_function.lambda_handler(event, {})
        self.assertEqual(data.get("Error"), "RestoreError")
        self.assertEqual(data.get("Cause"), "inaccessible-encryption-credentials")
        self.assertEqual(data.get("message"), self.mock_email_response["MessageId"])
    
    def test_email_failure(self, mock_client):
        mock_ses = mock_client.return_value
        mock_ses.send_email.side_effect = Exception("Timeout Exception")
        with self.assertRaises(Exception) as err:
            _ =  email_function.lambda_handler(self.event, {})
            self.assertEqual(err.exception, Exception("Timeout Exception"))