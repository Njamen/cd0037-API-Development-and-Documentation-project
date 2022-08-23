import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


db_user = 'postgres'
db_user_password = 'postgres'
db_host = 'localhost:5432'


def not_found_404_test_error(self ,res, data):
    self.assertEqual(res.status_code, 404)
    self.assertEqual(data.get("error"), 404)
    self.assertEqual(data.get("message"), "resource not found")

def bad_request_400_test_error(self ,res, data):
    self.assertEqual(res.status_code, 400)
    self.assertEqual(data.get("error"), 400)
    self.assertEqual(data.get("message"), "bad request")    


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = f"postgresql://{db_user}:{db_user_password}@{db_host}/{self.database_name}" 
        self.new_question = {"question":"The highest Cameroon mont", "answer":"Mont Cameroon", 
                             "difficulty":5 , "category":1}
        self.new_bad_question = {"qusestion":"The highest Cameroon mont", "answer":"Mont Cameroon", 
                             "difficulty":5 , "category":1}



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
        res = self.client().get('/categories')
        data =json.loads(res.data)  
        self.assertEqual(res.status_code, 200)
        self.assertTrue( "categories" in data )
        self.assertTrue( len(data.get("categories")))
            
    def test_400_error_get_categories(self):
        res = self.client().get('/categories/2')
        data =json.loads(res.data)
        not_found_404_test_error(self ,res, data)    

    def test_get_questions(self): 
        res = self.client().get('/questions')
        data =json.loads(res.data)  
        self.assertEqual(res.status_code, 200)
        self.assertTrue(("questions"  in data) and ("currentCategory"  in data) )
        self.assertTrue( ("totalQuestions"  in data) and ("categories"  in data) )
        self.assertTrue( len(data.get("categories")))
        self.assertTrue( len(data.get("questions")))


    def test_404_get_categories_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data) 
        not_found_404_test_error(self, res, data)

    def test_get_category_questions(self): 
        res = self.client().get('/categories/1/questions')
        data =json.loads(res.data)  
        self.assertEqual(res.status_code, 200)
        self.assertTrue(("questions"  in data) and ("currentCategory"  in data) )
        self.assertTrue( "totalQuestions"  in data )
        self.assertTrue( len(data.get("questions")))
    
    def test_404_error_get_category_questions(self):
        res = self.client().post('/categories/1s/questions')
        data =json.loads(res.data)
        not_found_404_test_error(self ,res, data)


    def test_get_quizzes(self): 
        res = self.client().post(
            '/quizzes' , 
            json={"previous_questions": [20], "quiz_category": 1}
        )
        data =json.loads(res.data)  
        self.assertEqual(res.status_code, 200)
        self.assertTrue( "question" in data )



    def test_bad_request_error_test_get_quizzes(self): 
        res = self.client().post('/quizzes' )
        data =json.loads(res.data)  
        bad_request_400_test_error(self ,res, data)


    def test_add_question(self): 
        res = self.client().post('/questions' , json=self.new_question)
        data =json.loads(res.data)  
        self.assertEqual(res.status_code, 200)

        
    def test_400_error_add_question(self):
        res = self.client().post('/questions' , json=self.new_bad_question)
        data =json.loads(res.data)
        bad_request_400_test_error(self ,res, data)


    def test_search_question(self): 
        res = self.client().post('/questions' , 
                json={"searchTerm":"what"}
        )
        data =json.loads(res.data)  
        self.assertEqual(res.status_code, 200)
        self.assertTrue( "questions" in data )
        self.assertTrue( "totalQuestions" in data )
        self.assertTrue( "currentCategory" in data )
    
    def test_400_error_search_question(self):
        res = self.client().post('/questions' , json={"searchTerm":""})
        data =json.loads(res.data)
        bad_request_400_test_error(self ,res, data)

    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data) 
        book = Question.query.filter(Question.id == 2).one_or_none() 
        self.assertEqual(res.status_code, 200)
        self.assertEqual(book, None)



    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data) 
        self.assertEqual(res.status_code, 404)











    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()