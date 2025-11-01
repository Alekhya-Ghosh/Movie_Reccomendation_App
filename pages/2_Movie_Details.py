import streamlit as st
import requests

# Set your API key directly here (replace with your actual key)
DEFAULT_API_KEY = "a966a1c4"

# Initialize ALL session state variables at the very beginning
if 'api_key' not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY
if 'movies' not in st.session_state:
    st.session_state.movies = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None
if 'selected_movie_title' not in st.session_state:
    st.session_state.selected_movie_title = None


class OMDbClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    def search_movies(self, title, year=None, movie_type=None):
        """Search for movies by title"""
        if not self.api_key or self.api_key == "your_actual_api_key_here":
            st.error("❌ Please enter a valid API key in the sidebar!")
            return []

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
                error_msg = data.get('Error', 'Unknown error')
                st.error(f"API Error: {error_msg}")
                return []
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")
            return []

    def get_movie_details(self, imdb_id):
        """Get detailed information about a specific movie"""
        if not self.api_key or self.api_key == "your_actual_api_key_here":
            return None

        params = {
            'apikey': self.api_key,
            'i': imdb_id,
            'plot': 'full'
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
            st.error(f"Error fetching movie details: {e}")
            return None

    def get_recommendations(self, favorite_movie_title, max_results=10):
        """Get movie recommendations based on a favorite movie"""
        if not self.api_key or self.api_key == "your_actual_api_key_here":
            return []

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


# Configure the page
st.set_page_config(
    page_title="Movie Recommendation App",
    page_icon="🎬",
    layout="wide"
)

# Sidebar for API key input
st.sidebar.title("🔑 API Configuration")

# API Key input with unique key
api_key = st.sidebar.text_input(
    "Enter your OMDB API Key:",
    value=st.session_state.api_key,
    type="password",
    help="Get your free API key from http://www.omdbapi.com/apikey.aspx",
    key="api_key_input_unique"
)

# Update session state when API key changes
if api_key != st.session_state.api_key:
    st.session_state.api_key = api_key

# Initialize OMDB client with the API key
@st.cache_resource
def get_omdb_client(api_key):
    return OMDbClient(api_key)

client = get_omdb_client(st.session_state.api_key)

# API Status
st.sidebar.markdown("### 📊 API Status")
if client.api_key and client.api_key != "your_actual_api_key_here":
    st.sidebar.success("✅ API Key Loaded")
    # Test the API key
    test_params = {'apikey': client.api_key, 's': 'test', 'type': 'movie'}
    try:
        response = requests.get("http://www.omdbapi.com/", params=test_params)
        if response.status_code == 200:
            st.sidebar.success("✅ API Key is valid!")
        else:
            st.sidebar.error("❌ API Key test failed")
    except:
        st.sidebar.warning("⚠️ Could not test API key")
else:
    st.sidebar.error("❌ Please enter a valid API key")

# App header
st.title("🎬 Movie Recommendation App")
st.markdown("Discover your next favorite movie based on your preferences!")

# Navigation in sidebar
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox(
    "Choose a mode",
    ["Movie Search", "Get Recommendations", "About"],
    key="app_mode_select"
)

# Show main content only if API key is available
if client.api_key and client.api_key != "your_actual_api_key_here":
    if app_mode == "Movie Search":
        st.header("🔍 Search for Movies")

        col1, col2 = st.columns([2, 1])

        with col1:
            search_query = st.text_input("Enter movie title:", placeholder="e.g., Inception", key="search_input_main")

        with col2:
            search_year = st.text_input("Year (optional):", placeholder="e.g., 2010", key="year_input_main")

        # Search button
        if st.button("Search Movies", key="search_btn_main") and search_query:
            with st.spinner("Searching for movies..."):
                movies = client.search_movies(search_query, search_year)
                if movies:
                    st.session_state.movies = movies
                    st.success(f"Found {len(movies)} movies!")
                else:
                    st.session_state.movies = []
                    st.error("No movies found. Please try a different search term.")

        # Display movies
        if st.session_state.movies:
            st.markdown("---")
            st.subheader("🎬 Search Results")

            # Display movies in a grid
            cols = st.columns(3)
            for i, movie in enumerate(st.session_state.movies):
                with cols[i % 3]:
                    with st.container():
                        # Movie card
                        st.write(f"### {movie['Title']}")

                        # Poster
                        if movie.get('Poster') and movie['Poster'] != 'N/A':
                            st.image(movie['Poster'], use_column_width=True)
                        else:
                            st.info("🎭 No poster available")

                        st.write(f"**Year:** {movie.get('Year', 'N/A')}")
                        st.write(f"**Type:** {movie.get('Type', 'N/A').title()}")

                        # FIXED: Use st.page_link instead of st.switch_page
                        if st.button(f"View Full Details", key=f"view_details_{i}"):
                            # Store the selected movie in session state
                            st.session_state.selected_movie_id = movie['imdbID']
                            st.session_state.selected_movie_title = movie['Title']
                            # Use page_link for navigation
                            st.page_link("pages/2_Movie_Details.py", label="Go to Movie Details", icon="🎬")

                        st.markdown("---")

    elif app_mode == "Get Recommendations":
        st.header("🎯 Get Movie Recommendations")

        col1, col2 = st.columns([2, 1])

        with col1:
            favorite_movie = st.text_input(
                "Enter your favorite movie:",
                placeholder="e.g., The Dark Knight",
                help="We'll find similar movies based on genre",
                key="fav_movie_input_main"
            )

        with col2:
            num_recommendations = st.slider(
                "Number of recommendations:",
                min_value=5,
                max_value=20,
                value=10,
                key="rec_slider_main"
            )

        if st.button("Get Recommendations", key="rec_btn_main") and favorite_movie:
            with st.spinner("Finding recommendations..."):
                recommendations = client.get_recommendations(favorite_movie, num_recommendations)
                if recommendations:
                    st.session_state.recommendations = recommendations
                    st.success(f"Found {len(recommendations)} recommendations!")
                else:
                    st.session_state.recommendations = []
                    st.error("No recommendations found. Please try a different movie.")

        # Display recommendations
        if st.session_state.recommendations:
            st.markdown("---")
            st.subheader("🎭 Recommended Movies")

            # Display recommendations in a grid
            cols = st.columns(2)
            for i, movie in enumerate(st.session_state.recommendations):
                with cols[i % 2]:
                    with st.container():
                        st.write(f"### {movie['Title']}")

                        # Movie poster and info in columns
                        col_img, col_info = st.columns([1, 2])

                        with col_img:
                            if movie.get('Poster') and movie['Poster'] != 'N/A':
                                st.image(movie['Poster'], use_column_width=True)
                            else:
                                st.info("📸 No poster")

                        with col_info:
                            st.write(f"**📅 Year:** {movie.get('Year', 'N/A')}")
                            st.write(f"**🎭 Genre:** {movie.get('Genre', 'N/A')}")
                            st.write(f"**🎬 Director:** {movie.get('Director', 'N/A')}")
                            st.write(f"**⭐ IMDB Rating:** {movie.get('imdbRating', 'N/A')}/10")
                            st.write(f"**⏱️ Runtime:** {movie.get('Runtime', 'N/A')}")

                        # FIXED: Use st.page_link instead of st.switch_page
                        if st.button(f"View Full Details", key=f"rec_view_{i}"):
                            # Store the selected movie in session state
                            st.session_state.selected_movie_id = movie['imdbID']
                            st.session_state.selected_movie_title = movie['Title']
                            # Use page_link for navigation
                            st.page_link("pages/2_Movie_Details.py", label="Go to Movie Details", icon="🎬")

                        # Plot summary in expander
                        if movie.get('Plot') and movie['Plot'] != 'N/A':
                            with st.expander("📖 Quick Plot Summary"):
                                st.write(movie['Plot'])

                        st.markdown("---")

    else:
        st.header("About This App")
        st.markdown("""
        ### 🎬 Movie Recommendation App

        Welcome to your personal movie discovery companion! This app helps you find amazing movies using the OMDB API.

        **✨ Features:**
        - **🔍 Movie Search**: Search for any movie by title and year
        - **🎯 Smart Recommendations**: Get personalized movie suggestions based on your favorites
        - **📊 Detailed Information**: View comprehensive details in separate pages
        - **🖼️ Movie Posters**: Browse through movie posters and visuals

        **🚀 How to use:**
        1. **Enter your API key** in the sidebar
        2. **Movie Search**: Enter a movie title to search the database
        3. **Get Recommendations**: Tell us your favorite movie and we'll suggest similar ones
        4. **Click "View Full Details"** to see complete movie information on a separate page

        **🎭 Data Source**: Powered by [OMDB API](http://www.omdbapi.com/)
        """)

else:
    st.error("🚨 API Key Required")
    st.markdown("""
    ### Please enter your OMDB API key in the sidebar to get started!

    **🔑 Get your FREE API key:**
    1. Visit [OMDB API](http://www.omdbapi.com/apikey.aspx)
    2. Choose the FREE plan
    3. Verify your email
    4. Copy your API key
    5. Paste it in the sidebar input field

    **🎯 What you'll get:**
    - Access to thousands of movies
    - Detailed movie information on separate pages
    - Personalized recommendations
    - High-quality movie posters
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OMDB API")