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



    CORS(app, resources={r"*" : {"origins": '*'}}) 


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response


    @app.route('/categories', methods=['GET'])
    def get_categories(): 
        return jsonify({'categories' : Category.get_all_formatted()})  



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



    @app.route('/questions/<int:id>',  methods=['DELETE'])
    def delete_question(id):
        question = Question.query.get_or_404(id)    
        try :
            question.delete() 
        except :   
            abort(422)
             
        return jsonify({"id":question.id}) 



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



    @app.route('/quizzes',  methods=['POST'])
    def get_quizzes():

        body = request.get_json()

        if body is None :
            abort(400)

        previous_questions = body.get('previous_questions',None) 
        category_id = body.get('quiz_category', None) 


        if previous_questions is None or category_id is None :
            abort(400)
        
        if category_id == 0 :
            query = Question.query.filter(~Question.id.in_(previous_questions))                        
        else :
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
    