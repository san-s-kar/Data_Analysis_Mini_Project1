import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

ratings_file = 'ratings.dat'
movies_file = 'movies.dat'
users_file = 'users.dat'

def load_ratings(file):
    ratings = []
    with open(file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            user_id, movie_id, rating, timestamp = line.strip().split("::")
            ratings.append((int(user_id), int(movie_id), float(rating)))
    return ratings

def load_movies(file):
    movies = {}
    with open(file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            movie_id, title, genres = line.strip().split("::")
            movies[int(movie_id)] = {'title': title, 'genres': genres.split("|")}
    return movies

def load_users(file):
    users = {}
    with open(file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            user_id, gender, age, occupation, _ = line.strip().split("::")
            users[int(user_id)] = {'gender': gender, 'age': int(age), 'occupation': int(occupation)}
    return users

ratings = load_ratings(ratings_file)
movies = load_movies(movies_file)
users = load_users(users_file)

# Dashboard Title with Emoji
st.markdown("<h1 style='text-align: center;'>🎬 Movie Data Dashboard 📊</h1>", unsafe_allow_html=True)

# Centered "Select Visualization" with Emoji
st.markdown("""
    <div style="display: flex; justify-content: center;">
        <h3>🔎 Select Visualization</h3>
    </div>
""", unsafe_allow_html=True)

# Visualization selector
selected_visualization = st.selectbox(
    "Select Visualization", 
    ["Distribution of Ratings by Genres and Years 📅", "Popular Genres by User Demographics 👥", "Heatmap of Genre Correlation 🔥"]
)

if selected_visualization == "Distribution of Ratings by Genres and Years 📅":
    st.subheader("Distribution of Ratings by Genres and Years")

    genre_ratings = defaultdict(list)
    year_ratings = defaultdict(list)

    for user_id, movie_id, rating in ratings:
        if movie_id in movies:
            movie = movies[movie_id]
            genres = movie['genres']
            for genre in genres:
                genre_ratings[genre].append(rating)
            if '(' in movie['title'] and ')' in movie['title']:
                year = movie['title'].split('(')[-1].replace(')', '')
                if year.isdigit():
                    year_ratings[int(year)].append(rating)

    # Average ratings by genre with a vertical bar chart
    avg_genre_ratings = {genre: np.mean(ratings) for genre, ratings in genre_ratings.items()}
    genres, avg_ratings = zip(*sorted(avg_genre_ratings.items(), key=lambda x: x[1], reverse=True))

    plt.figure(figsize=(10, 6))
    plt.bar(genres, avg_ratings, color='skyblue')
    plt.xlabel("Genre")
    plt.ylabel("Average Rating")
    plt.title("Average Ratings by Genre 🎥")
    plt.xticks(rotation=45, ha="right")  # Rotate genre labels for better readability
    st.pyplot(plt)

    # Average ratings by year with a vertical bar chart
    avg_year_ratings = {year: np.mean(ratings) for year, ratings in year_ratings.items()}
    years, avg_ratings = zip(*sorted(avg_year_ratings.items()))

    plt.figure(figsize=(10, 6))
    plt.bar(years, avg_ratings, color='green')
    plt.xlabel("Year 📆")
    plt.ylabel("Average Rating")
    plt.title("Average Ratings by Year 🗓️")
    st.pyplot(plt)

elif selected_visualization == "Popular Genres by User Demographics 👥":
    st.subheader("Popular Genres by User Demographics")

    gender_genre_ratings = {'M': defaultdict(list), 'F': defaultdict(list)}
    for user_id, movie_id, rating in ratings:
        if user_id in users and movie_id in movies:
            gender = users[user_id]['gender']
            genres = movies[movie_id]['genres']
            for genre in genres:
                gender_genre_ratings[gender][genre].append(rating)

    avg_gender_genre_ratings = {
        gender: {genre: np.mean(ratings) for genre, ratings in genre_ratings.items()}
        for gender, genre_ratings in gender_genre_ratings.items()
    }

    # Combine the gender-based average ratings into a single list for plotting
    all_genres = list(set(list(avg_gender_genre_ratings['M'].keys()) + list(avg_gender_genre_ratings['F'].keys())))
    avg_ratings_male = [avg_gender_genre_ratings['M'].get(genre, 0) for genre in all_genres]
    avg_ratings_female = [avg_gender_genre_ratings['F'].get(genre, 0) for genre in all_genres]

    # Set positions for the bars
    x = np.arange(len(all_genres))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(14, 6))

    # Create the grouped bar chart
    bars_male = ax.bar(x - width/2, avg_ratings_male, width, label='Male', color='orange')
    bars_female = ax.bar(x + width/2, avg_ratings_female, width, label='Female', color='purple')

    # Add some text for labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel('Genres 🎬')
    ax.set_ylabel('Average Rating 📊')
    ax.set_title('Average Ratings by Genre and Gender 👫')
    ax.set_xticks(x)
    ax.set_xticklabels(all_genres, rotation=45, ha='right')
    ax.legend()

    # Add value labels on top of the bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

    add_labels(bars_male)
    add_labels(bars_female)

    st.pyplot(fig)

elif selected_visualization == "Heatmap of Genre Correlation 🔥":
    st.subheader("Heatmap of Genre Correlation")

    genre_ratings = defaultdict(list)
    for _, movie_id, rating in ratings:
        if movie_id in movies:
            genres = movies[movie_id]['genres']
            for genre in genres:
                genre_ratings[genre].append(rating)

    genres = list(genre_ratings.keys())
    matrix = np.zeros((len(genres), len(genres)))

    for i, genre1 in enumerate(genres):
        for j, genre2 in enumerate(genres):
            if i <= j:
                common_ratings = min(len(genre_ratings[genre1]), len(genre_ratings[genre2]))
                correlation = np.corrcoef(
                    genre_ratings[genre1][:common_ratings], genre_ratings[genre2][:common_ratings]
                )[0, 1] if common_ratings > 1 else 0
                matrix[i][j] = matrix[j][i] = correlation

    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix, xticklabels=genres, yticklabels=genres, annot=False, cmap="coolwarm")
    plt.title("Correlation Between Genres 🔄")
    st.pyplot(plt)
