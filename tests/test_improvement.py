"""Tests for improvement crew."""

from unittest.mock import MagicMock, patch

import pytest

from autodoc_ai.crews.improvement import ImprovementCrew


class TestImprovementCrew:
    """Tests for ImprovementCrew."""

    def test_init_defaults(self):
        """Test improvement crew initialization with defaults."""
        crew = ImprovementCrew()
        assert crew.target_score == 85
        assert crew.max_iterations == 3
        assert crew.evaluation_crew is not None

    def test_init_custom(self):
        """Test improvement crew initialization with custom values."""
        crew = ImprovementCrew(target_score=90, max_iterations=5)
        assert crew.target_score == 90
        assert crew.max_iterations == 5

    def test_run_already_good_score(self, tmp_path):
        """Test when document already has good score."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Good Document\n\nWell written content.")
        
        crew = ImprovementCrew(target_score=80)
        
        # Mock the auto_improve_one method from parent class
        with patch.object(crew, 'auto_improve_one') as mock_improve:
            # Create a mock iterator object with the expected attributes
            mock_iterator = MagicMock()
            mock_iterator._iterations = [MagicMock(score=85)]
            mock_iterator.final_score = 85
            mock_iterator.total_improvement = 0
            mock_improve.return_value = mock_iterator
            
            result = crew.run(str(test_file))
            
            assert result["initial_score"] == 85
            assert result["final_score"] == 85
            assert result["iterations"] == 0  # len(_iterations) - 1
            assert result["target_reached"] is True

    def test_run_needs_improvement(self, tmp_path):
        """Test document that needs improvement."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Document\n\nNeeds improvement.")
        
        crew = ImprovementCrew(target_score=85, max_iterations=2)
        
        with patch.object(crew, 'auto_improve_one') as mock_improve:
            # Create a mock iterator object with the expected attributes
            mock_iterator = MagicMock()
            mock_iterator._iterations = [
                MagicMock(score=70),
                MagicMock(score=80),
                MagicMock(score=90)
            ]
            mock_iterator.final_score = 90
            mock_iterator.total_improvement = 20
            mock_improve.return_value = mock_iterator
            
            result = crew.run(str(test_file))
            
            assert result["initial_score"] == 70
            assert result["final_score"] == 90
            assert result["iterations"] == 2  # len(_iterations) - 1
            assert result["target_reached"] is True

    def test_run_max_iterations_reached(self, tmp_path):
        """Test when max iterations are reached."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Poor Document\n\nNeeds work.")
        
        crew = ImprovementCrew(target_score=95, max_iterations=2)
        
        with patch.object(crew, 'auto_improve_one') as mock_improve:
            # Create a mock iterator object with the expected attributes
            mock_iterator = MagicMock()
            mock_iterator._iterations = [
                MagicMock(score=60),
                MagicMock(score=70),
                MagicMock(score=75)
            ]
            mock_iterator.final_score = 75
            mock_iterator.total_improvement = 15
            mock_improve.return_value = mock_iterator
            
            result = crew.run(str(test_file))
            
            assert result["initial_score"] == 60
            assert result["final_score"] == 75
            assert result["iterations"] == 2  # len(_iterations) - 1
            assert result["target_reached"] is False

    def test_run_file_not_found(self):
        """Test when file doesn't exist."""
        crew = ImprovementCrew()
        
        result = crew.run("/nonexistent/file.md")
        
        assert result == {"error": "Document not found or empty: /nonexistent/file.md"}

    def test_run_with_output_dir(self, tmp_path):
        """Test run with custom output directory."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test\n\nContent")
        output_dir = tmp_path / "improved"
        
        crew = ImprovementCrew(target_score=80)
        
        with patch.object(crew, 'auto_improve_one') as mock_improve:
            # Create a mock iterator object with the expected attributes
            mock_iterator = MagicMock()
            mock_iterator._iterations = [MagicMock(score=85)]
            mock_iterator.final_score = 85
            mock_iterator.total_improvement = 0
            mock_improve.return_value = mock_iterator
            
            result = crew.run(str(test_file), output_dir=str(output_dir))
            
            assert result["target_reached"] is True

    def test_run_with_doc_type(self, tmp_path):
        """Test run with specified doc type."""
        test_file = tmp_path / "api.md"
        test_file.write_text("# API Reference\n\nEndpoints")
        
        crew = ImprovementCrew()
        
        with patch.object(crew, 'auto_improve_one') as mock_improve:
            # Create a mock iterator object with the expected attributes
            mock_iterator = MagicMock()
            mock_iterator._iterations = [MagicMock(score=75), MagicMock(score=85)]
            mock_iterator.final_score = 85
            mock_iterator.total_improvement = 10
            mock_improve.return_value = mock_iterator
            
            result = crew.run(str(test_file), doc_type="api")
            
            assert result["final_score"] == 85


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])