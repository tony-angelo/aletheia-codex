"""
Unit tests for unified authentication module.

Tests the unified authentication decorator that supports both IAP and Firebase Auth.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Request
import functools

# Import module under test
import sys
sys.path.append('/workspace')
from shared.auth import unified_auth


class TestGetUserIdFromRequest:
    """Tests for get_user_id_from_request function."""
    
    def test_iap_authentication_success(self):
        """Test successful authentication via IAP."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'valid.iap.token'
        }
        
        with patch('shared.auth.unified_auth.iap_auth.get_user_from_iap') as mock_iap:
            mock_iap.return_value = ('user@example.com', None)
            
            user_id, error = unified_auth.get_user_id_from_request(mock_request)
            
            assert user_id == 'user@example.com'
            assert error is None
            mock_iap.assert_called_once_with(mock_request)
    
    def test_firebase_authentication_success(self):
        """Test successful authentication via Firebase Auth."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'Authorization': 'Bearer firebase.token'
        }
        
        with patch('shared.auth.unified_auth.firebase_auth.get_user_id_from_request') as mock_firebase:
            mock_firebase.return_value = ('user@example.com', None)
            
            user_id, error = unified_auth.get_user_id_from_request(mock_request)
            
            assert user_id == 'user@example.com'
            assert error is None
            mock_firebase.assert_called_once_with(mock_request)
    
    def test_iap_priority_over_firebase(self):
        """Test that IAP is checked before Firebase Auth."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'iap.token',
            'Authorization': 'Bearer firebase.token'
        }
        
        with patch('shared.auth.unified_auth.iap_auth.get_user_from_iap') as mock_iap:
            mock_iap.return_value = ('iap-user@example.com', None)
            
            with patch('shared.auth.unified_auth.firebase_auth.get_user_id_from_request') as mock_firebase:
                mock_firebase.return_value = ('firebase-user@example.com', None)
                
                user_id, error = unified_auth.get_user_id_from_request(mock_request)
                
                # Should use IAP, not Firebase
                assert user_id == 'iap-user@example.com'
                mock_iap.assert_called_once()
                mock_firebase.assert_not_called()
    
    def test_iap_fails_no_fallback_to_firebase(self):
        """Test that if IAP header is present but fails, we don't fall back to Firebase."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'invalid.iap.token',
            'Authorization': 'Bearer firebase.token'
        }
        
        error_response = (Mock(), 401, {})
        
        with patch('shared.auth.unified_auth.iap_auth.get_user_from_iap') as mock_iap:
            mock_iap.return_value = (None, error_response)
            
            with patch('shared.auth.unified_auth.firebase_auth.get_user_id_from_request') as mock_firebase:
                user_id, error = unified_auth.get_user_id_from_request(mock_request)
                
                # Should return IAP error, not try Firebase
                assert user_id is None
                assert error == error_response
                mock_iap.assert_called_once()
                mock_firebase.assert_not_called()
    
    def test_no_authentication_headers(self):
        """Test authentication fails when no headers are present."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        
        with patch('shared.auth.unified_auth.jsonify') as mock_jsonify:
            mock_jsonify.return_value = Mock()
            
            user_id, error = unified_auth.get_user_id_from_request(mock_request)
            
            assert user_id is None
            assert error is not None
            response, status_code, headers = error
            assert status_code == 401
    
    def test_firebase_authentication_fails(self):
        """Test authentication fails when Firebase Auth fails."""
        mock_request = Mock(spec=Request)
        mock_request.headers = {
            'Authorization': 'Bearer invalid.token'
        }
        
        error_response = (Mock(), 401, {})
        
        with patch('shared.auth.unified_auth.firebase_auth.get_user_id_from_request') as mock_firebase:
            mock_firebase.return_value = (None, error_response)
            
            user_id, error = unified_auth.get_user_id_from_request(mock_request)
            
            assert user_id is None
            assert error == error_response


class TestRequireAuthDecorator:
    """Tests for require_auth decorator."""
    
    def test_cors_preflight_request(self):
        """Test that OPTIONS requests are handled without authentication."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'OPTIONS'
        
        @unified_auth.require_auth
        def test_function(request):
            return 'success'
        
        response = test_function(mock_request)
        
        # Should return CORS headers without calling authentication
        assert response[1] == 204
        assert 'Access-Control-Allow-Origin' in response[2]
    
    def test_successful_authentication_adds_user_id(self):
        """Test that successful authentication adds user_id to request."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'GET'
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'valid.token'
        }
        
        @unified_auth.require_auth
        def test_function(request):
            return f'user: {request.user_id}'
        
        with patch('shared.auth.unified_auth.get_user_id_from_request') as mock_auth:
            mock_auth.return_value = ('user@example.com', None)
            
            result = test_function(mock_request)
            
            assert result == 'user: user@example.com'
            assert mock_request.user_id == 'user@example.com'
    
    def test_authentication_failure_returns_error(self):
        """Test that authentication failure returns error response."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'GET'
        mock_request.headers = {}
        
        @unified_auth.require_auth
        def test_function(request):
            return 'should not reach here'
        
        error_response = (Mock(), 401, {})
        
        with patch('shared.auth.unified_auth.get_user_id_from_request') as mock_auth:
            mock_auth.return_value = (None, error_response)
            
            result = test_function(mock_request)
            
            assert result == error_response
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""
        @unified_auth.require_auth
        def test_function(request):
            """Test function docstring."""
            return 'success'
        
        assert test_function.__name__ == 'test_function'
        assert test_function.__doc__ == 'Test function docstring.'
    
    def test_post_request_with_authentication(self):
        """Test POST request with successful authentication."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'POST'
        mock_request.headers = {
            'Authorization': 'Bearer firebase.token'
        }
        
        @unified_auth.require_auth
        def test_function(request):
            return {'user_id': request.user_id}
        
        with patch('shared.auth.unified_auth.get_user_id_from_request') as mock_auth:
            mock_auth.return_value = ('user@example.com', None)
            
            result = test_function(mock_request)
            
            assert result == {'user_id': 'user@example.com'}
    
    def test_cors_headers_include_iap_header(self):
        """Test that CORS headers include X-Goog-IAP-JWT-Assertion."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'OPTIONS'
        
        @unified_auth.require_auth
        def test_function(request):
            return 'success'
        
        response = test_function(mock_request)
        headers = response[2]
        
        assert 'X-Goog-IAP-JWT-Assertion' in headers['Access-Control-Allow-Headers']


class TestAuthenticationIntegration:
    """Integration tests for authentication flow."""
    
    def test_full_iap_authentication_flow(self):
        """Test complete IAP authentication flow."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'GET'
        mock_request.headers = {
            'X-Goog-IAP-JWT-Assertion': 'valid.iap.token'
        }
        
        @unified_auth.require_auth
        def test_function(request):
            return {'authenticated': True, 'user': request.user_id}
        
        with patch('shared.auth.unified_auth.iap_auth.get_user_from_iap') as mock_iap:
            mock_iap.return_value = ('iap-user@example.com', None)
            
            result = test_function(mock_request)
            
            assert result['authenticated'] is True
            assert result['user'] == 'iap-user@example.com'
    
    def test_full_firebase_authentication_flow(self):
        """Test complete Firebase authentication flow."""
        mock_request = Mock(spec=Request)
        mock_request.method = 'POST'
        mock_request.headers = {
            'Authorization': 'Bearer firebase.token'
        }
        
        @unified_auth.require_auth
        def test_function(request):
            return {'authenticated': True, 'user': request.user_id}
        
        with patch('shared.auth.unified_auth.firebase_auth.get_user_id_from_request') as mock_firebase:
            mock_firebase.return_value = ('firebase-user@example.com', None)
            
            result = test_function(mock_request)
            
            assert result['authenticated'] is True
            assert result['user'] == 'firebase-user@example.com'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])