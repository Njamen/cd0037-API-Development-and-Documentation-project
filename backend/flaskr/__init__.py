import os
from sre_parse import CATEGORIES
from flask import Flask, request, abort, jsonify , make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_cors import CORS, cross_origin 

import random

from models import (
    setup_db, 
    Question, 
    Category 
)

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app, resources={r"*" : {"origins": '*'}}) 


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests 
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_categories(): 
        return jsonify({'categories' : Category.get_all_formatted()})  

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """


    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)         

        questions = Question.query.all()  
        total_questions = len(questions) 
        start = (page - 1) * QUESTIONS_PER_PAGE 
        end = start + QUESTIONS_PER_PAGE 
        if start >= len(questions) :
            abort(404) 
        categories = Category.get_all_formatted() 
        data = {
            'questions' : [  it.format() for it in questions[start:end]],
            'totalQuestions' : total_questions,
            'categories' : categories,
            'currentCategory' : categories.get(f"{page}")
        }
        return jsonify(data)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>',  methods=['DELETE'])
    def delete_question(id):
        question = Question.query.get_or_404(id)    
        try :
            question.delete() 
        except :   
            abort(422)
             
        return jsonify({"id":question.id}) 

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions',  methods=['POST'])
    def add_or_search_question(): 
        body = request.get_json()

        search_term = body.get('searchTerm', None)   


        if search_term is None :
            return  add_question(request)
        else :
            return  search_question(request) 



    def add_question(request):

        body = request.get_json()
        qt = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None) 

        if qt is None or answer is None or difficulty is None or category is None :
            abort(400) 

        try:
            question = Question(question=qt,answer=answer,category=category,difficulty=difficulty)
            question.insert()
        except:
            abort(422) 
        return jsonify({"id":question.id})


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    def search_question(request):

        body = request.get_json() 
        search_term = body.get('searchTerm', "") 

        if search_term is None or search_term =="" :
            abort(400)
        pattern = f"%{search_term}%" 
        found_questions = Question.query.filter(Question.question.ilike(pattern)).all()   

        if len(found_questions) == 0 :
            current_category = None
        else :
            current_category =found_questions[0].category                

        categories = Category.get_all_formatted() 
        data =  {
          'questions': [ it.format()   for it in found_questions ], 
          'totalQuestions': len(found_questions),
          'currentCategory':  categories.get(f"{current_category}")
        }         
        return jsonify(data)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions',  methods=['GET'])
    def get_category_questions(id): 
        categories = Category.get_all_formatted() 
        questions = Question.query.filter(Question.category == id).all()  
        total_questions = len(questions) 

        data = {
            'questions' : [  it.format() for it in questions],
            'totalQuestions' : total_questions,
            'currentCategory' : categories.get(f"{id}")
        }
        return jsonify(data)



    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes',  methods=['POST'])
    def get_quizzes():

        body = request.get_json()

        previous_questions = body.get('previous_questions',None) 
        category_id = body.get('quiz_category', None) 

        if previous_questions is None or category_id is None :
            abort(400)

        query = Question.query.filter( and_(
                            ~Question.id.in_(previous_questions),
                            Question.category == category_id
                             ) )

        found_question = query.limit(1).one_or_none()   

        if found_question is None :
            abort(404)

        data = {
            'question' : found_question.format() 
        }


        return jsonify(data)



    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "error" : 404,
            "message": "unprocessable"
        }), 422 

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error" : 404,
            "message": "resource not found"
        }) , 404


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error" : 400,
            "message": "bad request"
        }) , 400

    @app.errorhandler(500)
    def Internal_server_error(error):
        return jsonify({
            "error" : 500,
            "message": "Internal server error"
        }) , 500

        

    return app
    