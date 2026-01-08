"""
Tests for CRUD layer edge cases.
"""
import json
import pytest
from unittest.mock import patch
from app.schemas.quizzes import GeneratedQuiz, GeneratedQuestion
from app.schemas.user import User
import app.crud.quizzes as quizzes_crud


class TestQuizAccessControl:
    """Test quiz access control in CRUD layer."""

    def test_access_private_quiz_as_non_owner(self, client, auth_headers, created_quiz, setup_test_db):
        """Test that private quiz cannot be accessed by non-owner."""
        quiz_id = created_quiz["quiz_id"]
        
        # Register a second user
        second_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "full_name": "Other User",
            "password": "otherpass123"
        }
        client.post("/register", json=second_user_data)
        
        # Create a User object for the second user
        second_user = User(
            username="otheruser",
            email="other@example.com",
            full_name="Other User",
            disabled=False,
            language="en"
        )
        
        # Try to access quiz as non-owner (crud/quizzes.py line 31)
        quiz = quizzes_crud.get_quiz(quiz_id, second_user)
        
        # Should return None for private quiz accessed by non-owner
        assert quiz is None

    def test_access_public_quiz_as_non_owner(self, client, auth_headers, created_quiz, setup_test_db, test_user_data):
        """Test that public quiz can be accessed by non-owner."""
        quiz_id = created_quiz["quiz_id"]
        
        # Make the quiz public
        cursor = setup_test_db.cursor()
        cursor.execute(
            "UPDATE quizzes SET access = ? WHERE quiz_id = ?",
            ("public", quiz_id)
        )
        setup_test_db.commit()
        
        # Register a second user
        second_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "full_name": "Other User",
            "password": "otherpass123"
        }
        client.post("/register", json=second_user_data)
        
        # Create a User object for the second user
        second_user = User(
            username="otheruser",
            email="other@example.com",
            full_name="Other User",
            disabled=False,
            language="en"
        )
        
        # Should be able to access public quiz
        quiz = quizzes_crud.get_quiz(quiz_id, second_user)
        assert quiz is not None
        assert quiz.quiz_id == quiz_id


class TestQuizCreationEdgeCases:
    """Test edge cases in quiz creation."""

    def test_create_quiz_with_invalid_answer_index(self, setup_test_db):
        """Test creating quiz with invalid answer_index sets empty correct_answer."""
        # Create a quiz with invalid answer_index
        quiz_data = GeneratedQuiz(
            title="Test Quiz with Invalid Answer",
            questions=[
                GeneratedQuestion(
                    question="What is the capital of France?",
                    options=["London", "Paris", "Berlin", "Madrid"],
                    answer_index=10,  # Invalid: out of range
                    why_correct="Paris is the capital"
                ),
                GeneratedQuestion(
                    question="What is 2+2?",
                    options=["3", "4", "5"],
                    answer_index=-1,  # Invalid: negative
                    why_correct="Basic math"
                )
            ]
        )
        
        # Create the quiz (crud/quizzes.py lines 59-62)
        quiz = quizzes_crud.create_quiz(quiz_data, "testuser")
        
        # Both questions should have empty correct_answer due to invalid indices
        # Pydantic converts the dict to QuizQuestion objects, so access via attributes
        assert quiz.questions[0].correct_answer == ""
        assert quiz.questions[1].correct_answer == ""
        
        # Valid fields should still be set
        assert quiz.questions[0].answer_index == 10
        assert quiz.questions[1].answer_index == -1

    def test_create_quiz_with_valid_answer_index(self, setup_test_db):
        """Test creating quiz with valid answer_index sets correct_answer properly."""
        quiz_data = GeneratedQuiz(
            title="Test Quiz",
            questions=[
                GeneratedQuestion(
                    question="What is the capital of France?",
                    options=["London", "Paris", "Berlin", "Madrid"],
                    answer_index=1,  # Valid
                    why_correct="Paris is the capital"
                )
            ]
        )
        
        quiz = quizzes_crud.create_quiz(quiz_data, "testuser")
        
        # Should have correct_answer set to "Paris"
        # Access as Pydantic model attributes
        assert quiz.questions[0].correct_answer == "Paris"
        assert quiz.questions[0].answer_index == 1
