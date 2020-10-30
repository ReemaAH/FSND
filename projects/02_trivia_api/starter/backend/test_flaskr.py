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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

  
    def test_get_categories(self):
        """ Test get categories success """
        ## get response data
        response = self.client().get('/categories')
        ## check success value, status_code and if there is a categories list
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json.loads(response.data)['categories']))

    
    def test_questions_paginated_with_existed_page(self):
        """ Test question pagination success """
        ## get response data
        response = self.client().get('/questions?page=1')
  
        ## check success value, status_code 
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)

        ## check that total questions and questions retrived per page
        self.assertTrue(json.loads(response.data)['total_questions'])
        self.assertEqual(len(json.loads(response.data)['questions']), 10)
    

    def test_questions_paginated_with_not_existed_page(self):
        """ Test question pagination success """
        ## get response data
        response = self.client().get('/questions?page=99')
  
        ## check success value, status_code 
        self.assertFalse(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 404)


    def test_delete_a_question_success(self):
        """ Test delete question success """

        ## create a question obj
        question_test = Question(question='question', 
                                 answer='answer',
                                 category='category',
                                 difficulty=1)
        question_test.insert()
        ## get the number of questions before deleting the question obj
        questions_total_before = len(Question.query.all())
        ## send request to delete the newely created obj 
        response = self.client().delete('/questions/'+ format(question_test.id))
        ## get the number of questions after deleting the question obj
        questions_total_after = len(Question.query.all())

        ## check success value, status_code 
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)
        ## compare the questions_total_before and questions_total_after to check if the obj deleted or not
        self.assertFalse(questions_total_before == questions_total_after)
        self.assertTrue(questions_total_before > questions_total_after)
    

    def test_delete_a_question_failure(self):
        """ Test delete question failure """
        ## get response data
        response = self.client().delete('/questions/'+ format(100))

        ## check success value, status_code 
        self.assertFalse(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 422)
    

    def test_create_new_question_success(self):
        """ Test create a question obj success """
        ## get the number of questions before creating a new question obj
        questions_total_before = len(Question.query.all())

        ## create a question obj
        question_test = Question(question='question', 
                                 answer='answer',
                                 category='category',
                                 difficulty=1)
       
        ## load response data
        response = self.client().post('/questions', json=question_test.format())
     
        ## get the number of questions after creating a new question obj
        questions_total_after = len(Question.query.all())

        ## check success value, status_code 
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)

        ## compare the questions_total_before and questions_total_after to check if the obj deleted or not
        self.assertFalse(questions_total_before == questions_total_after)
        self.assertTrue(questions_total_before < questions_total_after)
    

    def test_create_new_question_failure(self):
        """ Test create a question obj failure """
        ## get the number of questions before creating a new question obj
        questions_total_before = len(Question.query.all())

        ## load response data
        response = self.client().post('/questions', json={
            'question': 'question', 
             'answer': 'answer',
             'category': 'category',
             'difficulty': None,
        })
        ## get the number of questions after creating a new question obj
        questions_total_after = len(Question.query.all())
        
        ## check success value, status_code 
        self.assertFalse(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 422)
        ## as no obj was created the questions_total_before should be equal questions_total_after
        self.assertTrue(questions_total_before == questions_total_after)
    

    def test_search_questions_success(self):
        """ Test search questions success """

        ## load response data
        response = self.client().post('/questions/search',
                                      json={'searchTerm': 'discovered'})

        ## check success value, status_code 
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)

        ## check result
        self.assertEqual(len(json.loads(response.data)['questions']), 1)


    def test_search_questions_failure(self):
        """ Test search questions failure """

        ## load response data
        response = self.client().post('/questions/search',
                                      json={'searchTerm': 'gf+-@##$'})

        ## check success value, status_code 
        self.assertFalse(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 404)

    
    def test_get_questions_for_a_category_success(self):
        """ Test get questions for a category success """
        ## load response data 
        response = self.client().get('/categories/1/questions')
 

        ## check success value, status_code and number of retirved questions
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json.loads(response.data)['questions']) > 0)

       
    def test_get_questions_for_a_category_failure(self):
        """ Test get questions for a category failure """ 

        ## load response data 
        response = self.client().get('/categories/99/questions')

        # check response status code and message
        self.assertFalse(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 404)
    

    def test_quizzes_succeess(self):
        """ Test quizzes succeess """
        response = self.client().post('/quizzes',
            json={'quiz_category': {'type': 'Art', 'id': '2'},
                  'previous_questions':  [13, 14] })


        ## check success value, status_code 
        self.assertTrue(json.loads(response.data)['success'])
        self.assertEqual(response.status_code, 200)
       
        ## check if the questions in response not equal to the previous_questions sent
        self.assertNotEqual(json.loads(response.data)['question']['id'], 13)
        self.assertNotEqual(json.loads(response.data)['question']['id'], 14)
    
    def test_quizzes_failure(self):
       """ Test quizzes failure """
       # send post request without empty json 
       response = self.client().post('/quizzes',
            json={'quiz_category': None,
                  'previous_questions': None})
       
       # check success value, status_code
       self.assertFalse(json.loads(response.data)['success'])
       self.assertEqual(response.status_code, 404)

                                         


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()