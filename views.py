from flask import Flask, render_template, request, redirect, url_for, json, jsonify
from game import Game

app = Flask(__name__)

@app.route('/',  methods=['GET', 'POST'])
def deal():
    """Start the game"""
    game= Game.deal('E', 10)
    # Send new game to template
    return render_template("game.html", game=game, messages='Welcome! Select a card from the wings and place on the timeline')


@app.route('/send_guess', methods=['GET', 'POST'])
def send_guess():
    """
    Runs when user makes a guess
    """
    # Get info from web app
    game_id = request.json['game_id'] # Unique id for the deck (int)
    guess_id = int(request.json['guess_id'].split('_')[1]) # index of movie in the wings user selected
    location_guess = int(request.json['location_id'].split('_')[1]) # Location on timeline user selected
    
    print('Location on timeline:')
    print(location_guess)
    
    # Pull up the game being played & make the move
    game = Game(game_id)
    game, messages = game.make_move(guess_id, location_guess)
    print(messages)
    var = render_template("body.html", game=game, messages=messages)
    return var
