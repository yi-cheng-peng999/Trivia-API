import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('postgres:1234', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        expect_categories =  {
            '1' : "Science",
            '2' : "Art",
            '3' : "Geography",
            '4' : "History",
            '5' : "Entertainment",
            '6' : "Sports" }
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['categories'], expect_categories)

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        expect_question = [
            {'answer': 'The Liver', 'category': 1, 'difficulty': 4, 'id': 20, 'question': 'What is the heaviest organ in the human body?'},
            {'answer': 'Alexander Fleming', 'category': 1, 'difficulty': 3, 'id': 21, 'question': 'Who discovered penicillin?'},
            {'answer': 'Blood', 'category': 1, 'difficulty': 4, 'id': 22, 'question': 'Hematology is a branch of medicine involving the study of what?'}
        ]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'], 3)
        self.assertEqual(data['currentCategory'], 'Science')

        for question in data['questions']:
            self.assertTrue(question in expect_question)

    def test_404_get_category_questions(self):
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found.')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'], 19)
        self.assertEqual(len(data['questions']), 10)

    def test_get_questions_pagination(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'], 19)
        self.assertEqual(len(data['questions']), 10)

    def test_404_get_questions_pagination(self):
        res = self.client().get('/questions?page=10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource not found.')

    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/120')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()