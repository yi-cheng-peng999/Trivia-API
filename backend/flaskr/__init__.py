import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/': {'origins': '*'}})

  '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @DONE:
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrieve_categories():
    categories = {str(category.id):category.type for category in Category.query.all()}
    if not categories:
      abort(404)

    return jsonify({
      'success': True,
      'categories': categories
    })


  '''
  @DONE:
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def retrieve_questions():
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = page*QUESTIONS_PER_PAGE

    questions = Question.query.order_by(Question.id).all()
    total = len(questions)
    select_questions = questions[start:end]
    select_questions = [question.format() for question in select_questions]
    categories = {str(category.id):category.type for category in Category.query.all()}

    if len(select_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': select_questions,
      'totalQuestions': total,
      'categories': categories
    })


  '''
  @DONE:
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def delete_question_by_id(q_id):
    try:
      question = Question.query.get(q_id)
      question.delete()
      return jsonify({
        'success': True,
        'delete_id': q_id
      })
    except:
      abort(422)


  '''
  @DONE:
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)
    if (new_question and new_answer and new_difficulty and new_category) is None:
      abort(422)

    try:
      question = Question(new_question, new_answer, new_category, new_difficulty)
      question.insert()
      return jsonify({
        'success': True,
        'q_id': question.id
      })
    except:
      abort(422)

  '''
  @DONE:
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def post_search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term:
      questions = Question.query.filter(Question.question.like('%{}%'.format(search_term))).all()
      questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': questions,
        'totalQuestions': len(questions)
      })
    else:
      abort(422)
  '''
  @DONE:
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def retrieve_questions_by_categories(cat_id):
    try:
      category = Category.query.get(cat_id)
      questions = Question.query.filter(Question.category==cat_id)
      questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': questions,
        'totalQuestions': len(questions),
        'currentCategory': category.type
      })
    except:
      abort(404)

  '''
  @DONE:
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def post_quizzes():
    body = request.get_json()
    if 'previous_questions' not in body or 'quiz_category' not in body:
      abort(422)

    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)['id']
    print(previous_questions)
    print(quiz_category)
    print(previous_questions and quiz_category)
    if quiz_category == 0:
      questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
    else:
      questions = Question.query.filter_by(category=quiz_category).filter(Question.id.notin_((previous_questions))).all()
    questions = [question.format() for question in questions]
    if questions:
      q_i = random.randrange(len(questions))
      return jsonify({
        'success': True,
        'question': questions[q_i]
      })
    else:
      abort(422)



  '''
  @DONE:
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return (
      jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request.'
      }), 400
    )

  @app.errorhandler(404)
  def not_found(error):
    return (
      jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found.'
      }), 404
    )

  @app.errorhandler(422)
  def unprocessable(error):
    return (
      jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable.'
      }), 422
    )

  @app.errorhandler(500)
  def internal_server_error(error):
    return (
      jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error.'
      }), 500
    )

  return app

    