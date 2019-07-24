import pandas as pd
import warnings
import random

easy_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
med_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
hard_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
imp_df = pd.read_csv('data/selected_films_easy.tsv', sep='\t', index_col=0)
# TODO: Replace above tsv files with respective difficulty files
# TODO: User can choose difficulty and deck size
# TODO: points system, multiplayer, save game
# TODO: Clean up javscript
# TODO: Clean up database
# TODO: Messages and game complete 

class Game:
    """
    An instance of a game w/ unqiue game id
    """
    def __init__(self, game_id):
        self.game_id = game_id
        # Game difficult defined by game id
        self.game_diff = game_id.split('_')[0]
        # deck size defined by game id
        self.deck_size = int(game_id.split('_')[1]) 
        # Cards in deck defined by game id
        self.deck_id = int(game_id.split('_')[2])
        # Get deck using random state & game difficulty from game id
        if self.game_diff == 'E':
            self.deck = easy_df.sample(self.deck_size, random_state=self.deck_id).reset_index(drop=True)
        elif self.game_diff == 'M':
            self.deck = med_df.sample(self.deck_size, random_state=self.deck_id).reset_index(drop=True)
        elif self.game_diff == 'H':
            self.deck = hard_df.sample(self.deck_size, random_state=self.deck_id).reset_index(drop=True)
        elif self.game_diff == 'I':
            self.deck = imp_df.sample(self.deck_size, random_state=self.deck_id).reset_index(drop=True)
        else:
            self.deck = easy_df.sample(self.deck_size, random_state=self.deck_id).reset_index(drop=True)
            warnings.warn('Invalid difficulty, using easy.', SyntaxWarning)
        # Game status defined by game id
        status = game_id.split('_')[3] 
        self.deck['status']=['T'] + list(status) + ['D'] * (self.deck_size-len(status)-1)
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
                               pd.to_datetime(compare_below['releaseDate']).strftime('%B, %-d') +\
                               ' and <i>' + to_place['primaryTitle'] +'</i> was released on ' + \
                               pd.to_datetime(to_place['releaseDate']).strftime('%B, %-d') + '.']
                
                if compare_below['releaseDate'] < to_place['releaseDate']:
                    messages = ['A close one, and you nailed it!'] + compare_str
                    """Code for close calls here"""
                elif compare_below['releaseDate'] > to_place['releaseDate']:
                    messages = ['Close enough!'] + compare_str
                else:
                    messages = ['Fun Fact!', '<i>' +
                                compare_below['primaryTitle'] + '</i> and <i>' + \
                                to_place['primaryTitle'] + '</i> were both released on ' + \
                                pd.to_datetime(compare_below['releaseDate']).strftime('%B, %-d')]
            elif compare_date_above == true_date:
                compare_str =  ['<i>' + compare_above['primaryTitle'] +\
                               '</i> was released on ' +\
                                pd.to_datetime(compare_above['releaseDate']).strftime('%B, %-d')+\
                               ' and <i>' + to_place['primaryTitle'] + \
                               '</i> was released on ' +\
                                pd.to_datetime(to_place['releaseDate']).strftime('%B, %-d') +'.']
                if to_place['releaseDate'] < compare_above['releaseDate']:
                    messages = ['A close one, and you nailed it!'] + compare_str
                    """Code for close calls here"""
                elif to_place['releaseDate'] > compare_above['releaseDate']:
                    messages = ['Close enough!'] + compare_str
                else:
                    messages = ['Fun Fact!', '<i>' +
                                compare_above['primaryTitle'] + '</i> and <i>' + \
                                 to_place['primaryTitle'] + '</i> were both released on ' + \
                                 pd.to_datetime(compare_above['releaseDate']).strftime('%B, %-d')]
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
        self.game_id = self.game_diff + '_' + format(self.deck_size, '03d') + '_' + \
        str(self.deck_id) + '_' + status_string[1:].rstrip('D')
        self.timeline = self.timeline.sort_values(by='releaseDate').reset_index(drop=True)
        return self, messages
    
    def deal(game_diff, deck_size):
        """
        Given a deck ID and game status string, define all game attributes
        """
        deck_size = deck_size 
        # Unqiue deck ID used to draw cards
        deck_id = random.randint(100000000,1000000000)
        # Game status contains deck size, deck ID and game status string
        game_id = game_diff + '_' + format(deck_size, '03d') + '_' + str(deck_id) +'_WWW'
        self = Game(game_id)
        return self
        
    