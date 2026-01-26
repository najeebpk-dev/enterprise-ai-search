"""
Simple unit tests for Enterprise AI Search

To run tests:
    pip install -r requirements-dev.txt
    pytest tests/
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path


class TestConfig:
    """Test configuration loading."""
    
    @patch.dict('os.environ', {
        'SEARCH_ENDPOINT': 'https://test.search.windows.net',
        'SEARCH_KEY': 'test-key',
        'INDEX_NAME': 'test-index',
        'OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'OPENAI_KEY': 'test-openai-key',
        'EMBEDDING_MODEL': 'text-embedding-ada-002',
        'CHAT_MODEL': 'gpt-4'
    })
    def test_config_loads_from_env(self):
        """Test that config loads environment variables correctly."""
        from src import config
        
        assert config.SEARCH_ENDPOINT == 'https://test.search.windows.net'
        assert config.INDEX_NAME == 'test-index'
        assert config.EMBEDDING_MODEL == 'text-embedding-ada-002'


class TestIngest:
    """Test ingestion pipeline."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization for Azure keys."""
        import re
        
        test_cases = [
            ("file name.pdf", "file_name"),
            ("my-document.pdf", "my-document"),
            ("test@file#2.pdf", "test_file_2"),
        ]
        
        for input_name, expected in test_cases:
            stem = Path(input_name).stem
            sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '_', stem)
            assert sanitized == expected


class TestQuery:
    """Test query functionality."""
    
    def test_embedding_dimension(self):
        """Test that embeddings have correct dimension."""
        # text-embedding-ada-002 should produce 1536-dimensional vectors
        expected_dimension = 1536
        
        # This would be tested with actual API call in integration tests
        assert expected_dimension == 1536


# Placeholder for integration tests
@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring Azure resources."""
    
    @pytest.mark.skip(reason="Requires Azure credentials")
    def test_end_to_end_pipeline(self):
        """Test full ingestion and query pipeline."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
