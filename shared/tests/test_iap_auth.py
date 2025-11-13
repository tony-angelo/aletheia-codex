"""
Unit tests for IAP authentication module.

Tests IAP JWT validation, user extraction, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Request
import json
import base64

# Import module under test
import sys
sys.path.append('/workspace')
from shared.auth import iap_auth


class TestValidateIapJwt:
    """Tests for validate_iap_jwt function."""
    
    def test_valid_jwt_token(self):
        """Test validation of a valid IAP JWT token."""
        # Mock the id_token.verify_token function
        with patch('shared.auth.iap_auth.id_token.verify_token') as mock_verify:
            mock_verify.return_value = {
                'iss': 'https://cloud.google.com/iap',
                'sub': 'accounts.google.com:123456',
                'email': 'user@example.com',
                'aud': '/projects/123/apps/test-app',
                'exp': 9999999999,
                'iat': 1234567890
            }
            
            result = iap_auth.validate_iap_jwt(
                'valid.jwt.token',
                '/projects/123/apps/test-app'
            )
            
            assert result['email'] == 'user@example.com'
            assert result['iss'] == 'https://cloud.google.com/iap'
            mock_verify.assert_called_once()
    
    def test_invalid_issuer(self):
        """Test validation fails with invalid issuer."""
        with patch('shared.auth.iap_auth.id_token.verify_token') as mock_verify:
            mock_verify.return_value = {
                'iss': 'https://invalid-issuer.com',
                'email': 'user@example.com'
            }
            
            with pytest.raises(Exception) as exc_info:
                iap_auth.validate_iap_jwt('token', '/projects/123/apps/test')
            
            assert 'Invalid issuer' in str(exc_info.value)
    
    def test_expired_token(self):
        """Test validation fails with expired token."""
        with patch('shared.auth.iap_auth.id_token.verify_token') as mock_verify:
            mock_verify.side_effect = ValueError('Token expired')
            
            with pytest.raises(Exception) as exc_info:
                iap_auth.validate_iap_jwt('expired.token', '/projects/123/apps/test')
            
            assert 'Invalid IAP token' in str(exc_info.value)
    
    def test_invalid_signature(self):
        """Test validation fails with invalid signature."""
        with patch('shared.auth.iap_auth.id_token.verify_token') as mock_verify:
            mock_verify.side_effect = ValueError('Invalid signature')
            
            with pytest.raises(Exception) as exc_info:
                iap_auth.validate_iap_jwt('invalid.token', '/projects/123/apps/test')
            
            assert 'Invalid IAP token' in str(exc_info.value)
    
    def test_missing_audience(self):
        """Test validation with missing audience parameter."""
        with patch('shared.auth.iap_auth.get_expected_audience') as mock_audience:
            mock_audience.return_value = '/projects/123/apps/test'
            
            with patch('shared.auth.iap_auth.id_token.verify_token') as mock_verify:
                mock_verify.return_value = {
                    'iss': 'https://cloud.google.com/iap',
                    'email': 'user@example.com'
                }
                
                result = iap_auth.validate_iap_jwt('token')
                
                assert result['email'] == 'user@example.com'
                mock_audience.assert_called_once()


class TestExtractUserFromIapToken:
    """Tests for extract_user_from_iap_token function."""
    
    def test_extract_email_success(self):
        """Test successful email extraction from token."""
        decoded_token = {
            'email': 'user@example.com',
            'sub': 'accounts.google.com:123456'
        }
        
        user_id = iap_auth.extract_user_from_iap_token(decoded_token)
        
        assert user_id == 'user@example.com'
    
    def test_missing_email_claim(self):
        """Test extraction fails when email claim is missing."""
        decoded_token = {
            'sub': 'accounts.google.com:123456'
        }
        
        with pytest.raises(Exception) as exc_info:
            iap_auth.extract_user_from_iap_token(decoded_token)
        
        assert 'missing email claim' in str(exc_info.value)
    
    def test_empty_email_claim(self):
        """Test extraction fails when email claim is empty."""
        decoded_token = {
            'email': '',
            'sub': 'accounts.google.com:123456'
        }
        
        with pytest.raises(Exception) as exc_info:
            iap_auth.extract_user_from_iap_token(decoded_token)
        
        assert 'missing email claim' in str(exc_info.value)


class TestGetUserFromIap:
    """Tests for get_user_from_iap function."""
    
    def test_successful_authentication(self):
        """Test successful IAP authentication."""
        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'valid.jwt.token'
        }
        
        # Mock validation and extraction
        with patch('shared.auth.iap_auth.validate_iap_jwt') as mock_validate:
            mock_validate.return_value = {
                'email': 'user@example.com',
                'iss': 'https://cloud.google.com/iap'
            }
            
            user_id, error = iap_auth.get_user_from_iap(mock_request)
            
            assert user_id == 'user@example.com'
            assert error is None
            mock_validate.assert_called_once_with('valid.jwt.token')
    
    def test_missing_iap_header(self):
        """Test authentication fails when IAP header is missing."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        
        with patch('shared.auth.iap_auth.jsonify') as mock_jsonify:
            mock_jsonify.return_value = Mock()
            
            user_id, error = iap_auth.get_user_from_iap(mock_request)
            
            assert user_id is None
            assert error is not None
            response, status_code, headers = error
            assert status_code == 401
    
    def test_invalid_jwt_token(self):
        """Test authentication fails with invalid JWT."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'invalid.token'
        }
        
        with patch('shared.auth.iap_auth.validate_iap_jwt') as mock_validate:
            mock_validate.side_effect = Exception('Invalid token')
            
            with patch('shared.auth.iap_auth.jsonify') as mock_jsonify:
                mock_jsonify.return_value = Mock()
                
                user_id, error = iap_auth.get_user_from_iap(mock_request)
                
                assert user_id is None
                assert error is not None
                response, status_code, headers = error
                assert status_code == 401
    
    def test_token_missing_email(self):
        """Test authentication fails when token is missing email."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'valid.token'
        }
        
        with patch('shared.auth.iap_auth.validate_iap_jwt') as mock_validate:
            mock_validate.return_value = {
                'iss': 'https://cloud.google.com/iap',
                'sub': 'accounts.google.com:123456'
            }
            
            with patch('shared.auth.iap_auth.extract_user_from_iap_token') as mock_extract:
                mock_extract.side_effect = Exception('Missing email')
                
                with patch('shared.auth.iap_auth.jsonify') as mock_jsonify:
                    mock_jsonify.return_value = Mock()
                    
                    user_id, error = iap_auth.get_user_from_iap(mock_request)
                    
                    assert user_id is None
                    assert error is not None


class TestGetExpectedAudience:
    """Tests for get_expected_audience function."""
    
    def test_audience_from_environment(self):
        """Test getting audience from environment variable."""
        with patch.dict('os.environ', {'IAP_AUDIENCE': '/projects/123/apps/test'}):
            audience = iap_auth.get_expected_audience()
            assert audience == '/projects/123/apps/test'
    
    def test_missing_audience_environment(self):
        """Test behavior when audience environment variable is missing."""
        with patch.dict('os.environ', {}, clear=True):
            audience = iap_auth.get_expected_audience()
            assert audience is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])