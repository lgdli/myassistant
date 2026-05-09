import json
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_tree_data():
    return {
        "doc_id": "test-doc-123",
        "doc_name": "Test Document",
        "doc_description": "A test document",
        "structure": {
            "name": "Root",
            "children": [
                {"name": "Chapter 1", "children": []},
                {"name": "Chapter 2", "children": []},
            ]
        },
        "pages": [
            {"page": 1, "content": "Page 1 content"},
            {"page": 2, "content": "Page 2 content"},
            {"page": 3, "content": "Page 3 content"},
        ]
    }


def test_parse_pages():
    from page_index_mcp.main import _parse_pages
    
    assert _parse_pages("1") == [1]
    assert _parse_pages("1-3") == [1, 2, 3]
    assert _parse_pages("1,3,5") == [1, 3, 5]
    assert _parse_pages("1-2,5") == [1, 2, 5]


def test_pageindex_get_structure(mock_tree_data, tmp_path):
    tree_file = tmp_path / "test_tree.json"
    tree_file.write_text(json.dumps(mock_tree_data))
    
    from page_index_mcp.main import _pageindex_get_structure
    
    result = _pageindex_get_structure({"tree_path": str(tree_file)})
    
    assert result["status"] == "success"
    assert "structure" in result
    assert result["doc_name"] == "Test Document"


def test_pageindex_get_pages(mock_tree_data, tmp_path):
    tree_file = tmp_path / "test_tree.json"
    tree_file.write_text(json.dumps(mock_tree_data))
    
    from page_index_mcp.main import _pageindex_get_pages
    
    result = _pageindex_get_pages({"tree_path": str(tree_file), "pages": "1-2"})
    
    assert result["status"] == "success"
    assert "Page 1" in result["content"]
    assert "Page 2" in result["content"]


def test_pageindex_get_pages_invalid_file():
    from page_index_mcp.main import _pageindex_get_pages
    
    result = _pageindex_get_pages({"tree_path": "/nonexistent/path.json", "pages": "1"})
    
    assert result["status"] == "error"
    assert "not found" in result["error"]


def test_pageindex_get_structure_invalid_file():
    from page_index_mcp.main import _pageindex_get_structure
    
    result = _pageindex_get_structure({"tree_path": "/nonexistent/path.json"})
    
    assert result["status"] == "error"
    assert "not found" in result["error"]