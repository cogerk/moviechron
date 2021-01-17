from flask import Flask, render_template, request, redirect, url_for, json, jsonify, request
from game import Game

app = Flask(__name__)

@app.route('/',  methods=['GET', 'POST'])
def setup_game():
    """Setup the game"""
    return render_template('index.html')

@app.route('/game',  methods=['GET', 'POST'])
def deal():
    """Start the game"""
    print(request.form)
    diff = request.form['difficulty']
    size = int(request.form['size'])
    game= Game.deal(diff, size)
    # Send new game to template
    messages=['1) Pick a movie that is \"In The Wings\"', '2) Click a currently highlighted blue area to place it in the timeline']
    return render_template('game.html', game=game, messages=messages)


@app.route('/send_guess', methods=['GET', 'POST'])
def send_guess():
    """
    Runs when user makes a guess
    """
    # Get info from web app
    game_id = request.json['game_id'] # Unique id for the deck
    guess_id = int(request.json['guess_id'].split('_')[1]) # index of movie in the wings user selected
    location_guess = int(request.json['location_id'].split('_')[1]) # Location on timeline user selected
    
    # Pull up the game being played & make the move
    game = Game(game_id)
    game, messages = game.make_move(guess_id, location_guess)
    print(game.game_id)
    var = render_template('body.html', game=game, messages=messages)
    return var
