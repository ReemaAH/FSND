import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def get_all_categories(): 
  # This function is to get all categories 
  # it was created for get_categories() and get_questions()
  # to avoid redundant code
  categories = Category.query.all()
  if len(categories) != 0:
    return {category.id: category.type for category in categories}
  else:
    return None

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  # set up CORS, allowing all origins
  cors = CORS(app, resources={'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/categories')
  # this endpoint to get all categories in the DB
  def get_categories():
    categories = get_all_categories()

    if len(categories) == 0:
            abort(404)
    else:
      return jsonify({
        'success': True,
        'categories': categories
        })


  def questions_pagination(request):
    # this fucntion is for question pagination 
    # 10 questions per page
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE 
    end = start + QUESTIONS_PER_PAGE 
    questions = Question.query.all()
    questions_for_current_page = questions[start:end]

    return questions_for_current_page

  @app.route('/questions')
  # this endpoint is to get questions and it uses
  # questions_pagination() function
  def get_questions():
    questions_for_current_page = questions_pagination(request)
    categories = get_all_categories()
    if len(questions_for_current_page) == 0 or not categories:
            abort(404)
    else:
      questions_for_current_page = [question.format() for question in questions_for_current_page]
      total_questions = db.session.query(Question).count() 
      categories = get_all_categories()
      return jsonify({
            'success': True,
            'questions': questions_for_current_page,
            'total_questions': total_questions,
            'categories': categories,
        })


  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
        })
    except:
      abort(422)

 
  @app.route("/questions", methods=['POST'])
  # this endpoint it to create a new question obj 
  # from post data
  def create_a_question():
    # here i checked first if the data is not empty
    if request.get_json()['question'] and request.get_json()['answer'] \
      and request.get_json()['difficulty'] and request.get_json()['category']:
      question = request.get_json()['question']
      answer = request.get_json()['answer']
      difficulty = request.get_json()['difficulty']
      category = request.get_json()['category']

      new_question = Question(
        question=question, answer=answer,
        difficulty=difficulty, category=category)
      new_question.insert()

      return jsonify({
        'success': True,
        'created': new_question.id
        })
    else:
      abort(422)


  @app.route("/questions/search", methods=['POST'])
  # this endpoint is to serach for a question
  # it takes a word from the post data and uses Question.query.filter()
  # to get the result
  def search_for_a_question():
    if request.get_json()['searchTerm']:
      search_term = request.get_json()['searchTerm']
      result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      # here i checked if there is a result 
      if len(result) != 0:
        formatted_result = [question.format() for question in result]
        total_questions = len(formatted_result)

        return jsonify({
          'success': True,
          'questions': formatted_result,
          'total_questions': total_questions,
              })
      else:
        abort(404)


  @app.route("/categories/<int:category_id>/questions")
  # this endpoint is to get questions per category
  def get_questions_for_a_category(category_id):
    questions = Question.query.filter_by(category=str(category_id)).all()
    # if the questions not empty
    if len(questions) != 0:
      formatted_questions = [question.format() for question in questions]
      total_questions = len(formatted_questions)

      return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': total_questions,
          'current_category': category_id
      })
    else:
      abort(404)
    

  @app.route('/quizzes', methods=['POST'])
  # this endpoint to get questions to play the quiz. 
  # it takes category and previous question from post data
  # and return a random questions within the given category,
 
  def quiz():
    if request.get_json()['quiz_category'] is not None and request.get_json()['previous_questions'] is not None:
      quiz_category = request.get_json()['quiz_category']
      previous_questions = request.get_json()['previous_questions']
      # check the id of category
      if quiz_category['id'] != 0:
        # here i filter the quetions to be in the given category and i use notin_() to exclude the previous_questions
        questions = Question.query.filter(Question.category==quiz_category['id'],  Question.id.notin_((previous_questions))).all()
      else:
        # if no category was given then, i excluded only the previous_questions
        questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      if len(questions) != 0:
        # here i use random.randint() to get a random index
        random_question = questions[random.randint(0, len(questions)-1)]
        return jsonify({
          'success': True,
          'question': random_question.format()
        })
      else:
        abort(404)

    else:
      abort(404)

  ## errorhandler for 404
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404
  

  ## errorhandler for 422
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  return app

    