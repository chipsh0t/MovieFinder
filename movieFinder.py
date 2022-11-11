"""
Application main file
"""
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from mainPage import Ui_MainWindow
import sys
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


class MovieFinder(QtWidgets.QMainWindow):
    def __init__(self):
        #initializing UI
        #super(MovieFinder,self).__init__()
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #saves movie choices
        self.movie_rec = None
        #pandas DF, saves data which is read from the database
        self.df = None
        self.read_data()
        #adding choices for combobox objects
        self.add_actor_options()
        self.add_director_options()
        self.add_genre_options()
        #In the beginning search categories are disabled
        self.ui.actorBox.setEnabled(False)
        self.ui.directorBox.setEnabled(False)
        self.ui.genreBox.setEnabled(False) 
        #setting search options according to the user`s actions
        self.ui.restrictBox.activated.connect(self.restrict_search)
    
    def read_data(self):
        """
            Reads data from a SQLite db and loads it into a DataFrame
        """
        conn = sqlite3.connect('moviesDB.db')
        self.df = pd.read_sql_query("SELECT * FROM movies",conn)
        conn.close()
        
    def add_actor_options(self):
        """
            Loading actor data in actorBox
        """
        actor_list = sorted(list(set(self.df['Actors'].apply(lambda x: x.split(',')).sum())))
        self.ui.actorBox.addItems(actor_list)

    def add_director_options(self):
        """
            Loading director data in directorBox
        """
        director_list = sorted(list(set(self.df['Director'])))
        self.ui.directorBox.addItems(director_list)

    def add_genre_options(self):
        """
            Loading genre data in genreBox
        """
        genre_list = sorted(list(set(self.df['Genre'].apply(lambda x: x.split(',')).sum())))
        self.ui.genreBox.addItems(genre_list)
    
    def restrict_search(self):
        """
            Changing button/field avilability and functions according to the user`s choice
        """
        user_req = self.ui.restrictBox.currentText()
        if user_req == "Actor":
            #Search by actor, different search options are disabled, search button executes suggest_by_actor method
            self.ui.actorBox.setEnabled(True)
            self.ui.directorBox.setEnabled(False)
            self.ui.genreBox.setEnabled(False)
            try:
                self.ui.searchButton.clicked.disconnect()
            except TypeError:
                pass
            self.ui.searchButton.clicked.connect(self.suggest_by_actor)
        elif user_req == "Director":
            #Search by director, different search options are disabled, search button executes suggest_by_director method
            self.ui.actorBox.setEnabled(False)
            self.ui.directorBox.setEnabled(True)
            self.ui.genreBox.setEnabled(False)
            try:
                self.ui.searchButton.clicked.disconnect()
            except TypeError:
                pass
            self.ui.searchButton.clicked.connect(self.suggest_by_director)
        elif user_req == "Genre":
            #Search by genre, different search options are disabled, search button executes suggest_by_genre method
            self.ui.actorBox.setEnabled(False)
            self.ui.directorBox.setEnabled(False)
            self.ui.genreBox.setEnabled(True)
            try:
                self.ui.searchButton.clicked.disconnect()
            except TypeError:
                pass
            self.ui.searchButton.clicked.connect(self.suggest_by_genre)
        else:
            #using all 3 options of search(Actor, director, genre). Every option field is activated, search button execute suggest_by_all method
            self.ui.actorBox.setEnabled(True)
            self.ui.directorBox.setEnabled(True)
            self.ui.genreBox.setEnabled(True)
            try:
                self.ui.searchButton.clicked.disconnect()
            except TypeError:
                pass
            self.ui.searchButton.clicked.connect(self.suggest_by_all)

    def suggest_by_actor(self):
        """
            Search with actor
        """
        self.movie_rec = self.df[self.df['Actors'].str.contains(self.ui.actorBox.currentText())]
        self.show_visuals()

    def suggest_by_director(self):
        """
            Search with director
        """
        self.movie_rec = self.df[self.df['Director'].str.contains(self.ui.directorBox.currentText())]
        self.show_visuals()

    def suggest_by_genre(self):
        """
            Search with genre
        """
        self.movie_rec = self.df[self.df['Genre'].str.contains(self.ui.genreBox.currentText())]
        self.show_visuals()

    def suggest_by_all(self):
        """
            Search by all actor, director and choice
        """
        actor_choice, director_choice, genre_choice = self.ui.actorBox.currentText(), self.ui.directorBox.currentText(), self.ui.genreBox.currentText()
        self.movie_rec = self.df[self.df['Genre'].str.contains(genre_choice) & self.df['Director'].str.contains(director_choice) & self.df['Actors'].str.contains(actor_choice)]
        self.show_visuals()
    
    def show_visuals(self):
        """
            Visualising the results. If the result is empty, user will be notified
        """
        if self.movie_rec.empty:
            #In case of an empty result
            msg = QMessageBox()
            msg.setWindowTitle("Results")
            msg.setText("No results found for your search !")
            msg.setIcon(QMessageBox.Information)
            show_msg = msg.exec_()
        else:
            #dividing the figure into 2 parts
            fig,(ax1, ax2) = plt.subplots(2,1)
            #adding horizontal space
            fig.subplots_adjust(hspace=0.5)
            #graph for IMDB ratings
            imdb_rating = self.movie_rec[:5].sort_values(by='IMDB_Rating',ascending=False)
            ax1.bar(imdb_rating['Series_Title'], imdb_rating['IMDB_Rating'])
            ax1.set_xlabel('')
            ax1.set_ylabel('IMDB ratings')
            #rotate the parameters
            ax1.tick_params('x', labelrotation=30)
            #graph for Meta scores
            meta_scores = self.movie_rec[:5].sort_values(by='Meta_score',ascending=False)
            ax2.stem(meta_scores['Series_Title'], meta_scores['Meta_score'])
            ax2.set_xlabel('')
            ax2.set_ylabel('Meta scores')
            ax2.tick_params('x', labelrotation=30)
            fig.tight_layout()
            plt.show()


def main():
    app = QtWidgets.QApplication([])
    application = MovieFinder()
    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 