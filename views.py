from flask import Flask
from flask import render_template
import pandas as pd

films_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
n = 14
deck = films_df.sample(n=10)



app = Flask(__name__)

@app.route('/')
def hello_world():
    # Select first card
    deck_loc = 0
    timeline = deck.iloc[deck_loc:deck_loc+1].reset_index()
    deck_loc = deck_loc +1    
    
    # Init Wings
    wings = deck.iloc[deck_loc:deck_loc+3].reset_index()
    deck_loc = deck_loc +3
    
    return render_template("game.html", 
                           timeline= timeline,
                           wings = wings
                          )

