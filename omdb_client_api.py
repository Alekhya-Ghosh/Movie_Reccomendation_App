import requests
import os
from dotenv import load_dotenv

load_dotenv()


class OMDbClient:
    def __init__(self):
        self.api_key = os.getenv('a966a1c4')
        self.base_url = "http://www.omdbapi.com/"

    def search_movies(self, title, year=None, movie_type=None):
        """Search for movies by title"""
        params = {
            'apikey': self.api_key,
            's': title,
            'type': movie_type or 'movie'
        }

        if year:
            params['y'] = year

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('Response') == 'True':
                return data['Search']
            else:
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

    def get_movie_details(self, imdb_id):
        """Get detailed information about a specific movie"""
        params = {
            'apikey': self.api_key,
            'i': imdb_id,
            'plot': 'short'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('Response') == 'True':
                return data
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movie details: {e}")
            return None

    def get_recommendations(self, favorite_movie_title, max_results=10):
        """Get movie recommendations based on a favorite movie"""
        # Search for the favorite movie
        search_results = self.search_movies(favorite_movie_title)

        if not search_results:
            return []

        # Get details of the first result
        favorite_movie = self.get_movie_details(search_results[0]['imdbID'])

        if not favorite_movie:
            return []

        # Search for similar movies based on genre
        genre = favorite_movie.get('Genre', '').split(',')[0] if favorite_movie.get('Genre') else ''
        year = favorite_movie.get('Year', '')[:4]  # Get just the year

        if genre:
            # Search by genre
            similar_movies = self.search_movies(genre)

            # Filter out the original movie and limit results
            recommendations = []
            for movie in similar_movies:
                if movie['imdbID'] != favorite_movie['imdbID'] and len(recommendations) < max_results:
                    # Get detailed information for each recommendation
                    movie_details = self.get_movie_details(movie['imdbID'])
                    if movie_details:
                        recommendations.append(movie_details)

            return recommendations

        return []