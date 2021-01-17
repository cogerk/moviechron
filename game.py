import pandas as pd
import warnings
import random

easy_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
medi_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
hard_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
impo_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
# TODO: Fix spacing #Big poster, text on hover w/ alpha
# TODO: Replace above tsv files with respective difficulty files
#Exception if release date’s year doesn’t match startYear
#Algorithm for more evenly spread release dates 
# TODO: points system, 
# TODO: multiplayer, 
# TODO: save game
# TODO: Clean up database
# TODO: Game complete 
#In the wings = On Deck


def build_deck(game_id, difficulty, deck_size):
    if difficulty == 'E':
        all_movies = easy_df#.sample(self.deck_size, random_state=self.deck_id).reset_index(drop=True)
    elif difficulty == 'M':
        all_movies = medi_df
    elif difficulty == 'H':
        all_movies = hard_df
    elif difficulty == 'I':
        all_movies = impo_df
    else:
        all_movies = easy_df
        warnings.warn('Invalid difficulty, using easy.', SyntaxWarning)
    deck= all_movies.sample(deck_size+1, random_state=game_id).reset_index(drop=True)
    #years = deck.startYear.unique().sample(self.deck_size, random_state=self.deck_id)
    
    return deck

class Game:
    """
    An instance of a game w/ unqiue game id
    """
    def __init__(self, game_id):
        self.game_id = game_id
        # Game difficult defined by game id
        self.difficulty = game_id.split('_')[0]
        # deck size defined by game id
        self.deck_size = int(game_id.split('_')[1]) 
        # Cards in deck defined by game id
        self.deck_id = int(game_id.split('_')[2])
        # Get deck using random state & game difficulty from game id
        self.deck = build_deck(self.deck_id, self.difficulty, self.deck_size)
        for col in self.deck: 
            print(col) 
        # Game status defined by game id
        status = game_id.split('_')[3] 
        print(['T'] + list(status) + ['D'] * (self.deck_size-len(status)-1))
        self.deck['status']=['T'] + list(status) + ['D'] * (self.deck_size-len(status))
        self.deck_loc = len(status)+1 
        # 'T' means the card is in the timeline
        self.timeline = self.deck[self.deck['status'] == 'T'].reset_index(drop=True)
        # 'W' means the card is in the wings
        self.wings = self.deck[self.deck['status'] == 'W'].reset_index(drop=True)
    
        
    def make_move(self, wing_select, location_guess):
        """
        Given user selection from wings and guessed location, determine if guess is correct
        """
        self.timeline = self.timeline.sort_values(by='releaseDate').reset_index(drop=True)
        # Get date of selected movie from the wings
        to_place = self.wings.iloc[int(wing_select)]
        true_date = to_place['startYear']

        
        # Determine acceptable date range from location guess
        if location_guess <= 0:
            compare_date_below = -float('inf')
            compare_date_above = int(self.timeline.iloc[0]['startYear'])
            compare_above = self.timeline.iloc[0]
        elif location_guess > (len(self.timeline)-1):
            compare_below = self.timeline.iloc[len(self.timeline)-1]
            compare_date_below = int(self.timeline.iloc[len(self.timeline)-1]['startYear'])
            compare_date_above = float('inf')
        else:
            compare_below = self.timeline.iloc[location_guess-1]
            compare_above = self.timeline.iloc[location_guess]
            compare_date_below = int(self.timeline.iloc[location_guess-1]['startYear'])
            compare_date_above = int(self.timeline.iloc[location_guess]['startYear'])
        # Determine if guess is correct
        if compare_date_below <= true_date <= compare_date_above:
            # Update Timeline & deck status if guess correct
            self.timeline = self.timeline.append(to_place)
            # 'T' means the card is in the timeline
            self.deck.loc[to_place.tconst == self.deck.tconst, 'status'] = 'T'
            """
            Game status update
            """ 
            # If same year, compare on release date for fun
            if compare_date_below == true_date:
                """Code for close ones"""
                compare_str = ['<i>' + compare_below['primaryTitle'] + \
                               '</i> was released on ' + \
                               pd.to_datetime(compare_below['releaseDate']).strftime('%x') +\
                               ' and <i>' + to_place['primaryTitle'] +'</i> was released on ' + \
                               pd.to_datetime(to_place['releaseDate']).strftime('%x') + '.']
                
                if compare_below['releaseDate'] < to_place['releaseDate']:
                    messages = ['A close one, and you nailed it!'] + compare_str
                    """Code for close calls here"""
                elif compare_below['releaseDate'] > to_place['releaseDate']:
                    messages = ['Close enough!'] + compare_str
                else:
                    messages = ['Fun Fact!', '<i>' +
                                compare_below['primaryTitle'] + '</i> and <i>' + \
                                to_place['primaryTitle'] + '</i> were both released on ' + \
                                pd.to_datetime(compare_below['releaseDate']).strftime('%x')]
            elif compare_date_above == true_date:
                compare_str =  ['<i>' + compare_above['primaryTitle'] +\
                               '</i> was released on ' +\
                                pd.to_datetime(compare_above['releaseDate']).strftime('%x')+\
                               ' and <i>' + to_place['primaryTitle'] + \
                               '</i> was released on ' +\
                                pd.to_datetime(to_place['releaseDate']).strftime('%x') +'.']
                if to_place['releaseDate'] < compare_above['releaseDate']:
                    messages = ['A close one, and you nailed it!'] + compare_str
                    """Code for close calls here"""
                elif to_place['releaseDate'] > compare_above['releaseDate']:
                    messages = ['Close enough!'] + compare_str
                else:
                    messages = ['Fun Fact!', '<i>' +
                                compare_above['primaryTitle'] + '</i> and <i>' + \
                                 to_place['primaryTitle'] + '</i> were both released on ' + \
                                 pd.to_datetime(compare_above['releaseDate']).strftime('%x')]
            else:
                messages = ['Great Work!']
        else:
            # Update deck status if incorrect
            messages = ['Nope.', 
                        '<i>'+to_place['primaryTitle']+'</i> came out in ' + \
                        str(int(true_date))]
            # 'I' means the card is discarded because of incorrect guess
            self.deck.loc[to_place.tconst == self.deck.tconst, 'status'] = 'I'
            """
            Losing points code here
            """
        # Draw a new card
        self.wings.drop(int(wing_select), inplace=True)
        if self.deck_loc < (self.deck_size-1):
            self.deck.loc[self.deck_loc, 'status'] = 'W'
            self.deck_loc = self.deck_loc + 1
            self.wings = self.deck[self.deck['status'] == 'W']
            self.wings = self.wings.reset_index(drop=True)

        else:
            self.wings.reset_index(drop=True, inplace=True)
        
        # Update status string & sort timeline
        status_string = ''.join(list(self.deck.status))
        self.game_id = self.difficulty + '_' + format(self.deck_size, '03d') + '_' + \
        str(self.deck_id) + '_' + status_string[1:].rstrip('D')
        self.timeline = self.timeline.sort_values(by='releaseDate').reset_index(drop=True)
        return self, messages
    
    def deal(difficulty, deck_size):
        """
        Given a deck ID and game status string, define all game attributes
        """
        deck_size = deck_size 
        
        # Unqiue deck ID used to draw cards
        deck_id = random.randint(100000000, 1000000000)
        # Game status contains deck size, deck ID and game status string
        game_id = difficulty + '_' + format(deck_size, '03d') + '_' + str(deck_id) +'_WWW'+ 'D' * (deck_size-3)
        self = Game(game_id)
        return self
        
    