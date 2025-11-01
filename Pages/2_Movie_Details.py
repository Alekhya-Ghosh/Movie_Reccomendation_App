import streamlit as st
import requests

# Configure the page
st.set_page_config(
    page_title="Movie Details",
    page_icon="🎭",
    layout="wide"
)

# Check if session state variables exist, if not initialize them
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None


st.title("🎭 Movie Details")

# Check if we have a selected movie
if 'selected_movie_id' not in st.session_state:
    st.error("🚫 No movie selected!")
    st.info("Please go back to the main page and click 'View Full Details' on a movie.")
    if st.button("🏠 Go to Home Page"):
        st.switch_page("app.py")
    st.stop()

# Check if we have an API key
if 'api_key' not in st.session_state or not st.session_state.api_key:
    st.error("🔑 API Key not found!")
    st.info("Please go back to the main page and enter your API key.")
    if st.button("🏠 Go to Home Page"):
        st.switch_page("app.py")
    st.stop()


# Create OMDb client class directly in this file
class OMDbClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    def get_movie_details(self, imdb_id):
        """Get detailed information about a specific movie"""
        if not self.api_key:
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
                st.error(f"API Error: {data.get('Error', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching movie details: {e}")
            return None


# Initialize client with the API key from session state
client = OMDbClient(st.session_state.api_key)

# Get movie details
with st.spinner("🎬 Loading movie details..."):
    movie_details = client.get_movie_details(st.session_state.selected_movie_id)

if movie_details:
    # Display movie details in a beautiful layout
    col1, col2 = st.columns([1, 2])

    with col1:
        # Poster
        if movie_details.get('Poster') and movie_details['Poster'] != 'N/A':
            st.image(movie_details['Poster'], use_column_width=True)
        else:
            st.info("🎭 No poster available")

        # Quick facts box
        st.markdown("### 📊 Quick Facts")
        st.write(f"**Year:** {movie_details.get('Year', 'N/A')}")
        st.write(f"**Rated:** {movie_details.get('Rated', 'N/A')}")
        st.write(f"**Released:** {movie_details.get('Released', 'N/A')}")
        st.write(f"**Runtime:** {movie_details.get('Runtime', 'N/A')}")
        st.write(f"**Genre:** {movie_details.get('Genre', 'N/A')}")
        st.write(f"**IMDB Rating:** ⭐ {movie_details.get('imdbRating', 'N/A')}/10")
        st.write(f"**IMDB Votes:** {movie_details.get('imdbVotes', 'N/A')}")

        if movie_details.get('BoxOffice') and movie_details['BoxOffice'] != 'N/A':
            st.write(f"**Box Office:** {movie_details.get('BoxOffice', 'N/A')}")

        if movie_details.get('DVD') and movie_details['DVD'] != 'N/A':
            st.write(f"**DVD Release:** {movie_details.get('DVD', 'N/A')}")

    with col2:
        # Main movie info
        st.header(movie_details['Title'])
        st.write(f"*{movie_details.get('Released', 'N/A')}*")

        # Ratings
        if movie_details.get('Ratings'):
            st.markdown("### 🏆 Ratings")
            for rating in movie_details['Ratings']:
                st.write(f"**{rating['Source']}:** {rating['Value']}")

        # Plot
        st.markdown("### 📖 Plot")
        st.write(movie_details.get('Plot', 'No plot available'))

        # Crew and Cast
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### 🎬 Crew")
            st.write(f"**Director:** {movie_details.get('Director', 'N/A')}")
            st.write(f"**Writer:** {movie_details.get('Writer', 'N/A')}")

        with col4:
            st.markdown("### 🎭 Cast")
            st.write(f"**Actors:** {movie_details.get('Actors', 'N/A')}")

        # Additional info
        st.markdown("### ℹ️ Additional Information")
        st.write(f"**Language:** {movie_details.get('Language', 'N/A')}")
        st.write(f"**Country:** {movie_details.get('Country', 'N/A')}")
        st.write(f"**Awards:** {movie_details.get('Awards', 'N/A')}")

        if movie_details.get('Production') and movie_details['Production'] != 'N/A':
            st.write(f"**Production:** {movie_details.get('Production', 'N/A')}")

        # IMDb ID
        st.write(f"**IMDb ID:** {movie_details.get('imdbID', 'N/A')}")
else:
    st.error("❌ Could not load movie details. Please try again.")
    st.info("This might be due to:")
    st.write("- Invalid API key")
    st.write("- Network connection issues")
    st.write("- Movie ID not found in database")

# Back button
st.markdown("---")
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔙 Back to Search", use_container_width=True, key="back_btn_details"):
        st.switch_page("app.py")
with col2:
    if st.button("🔄 Try Again", use_container_width=True, key="retry_btn_details"):
        st.rerun()

# Sidebar navigation
st.sidebar.markdown("---")
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/2_Movie_Details.py", label="Movie Details", icon="🎭", disabled=True)