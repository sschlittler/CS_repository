# Welcome to the Code of our Streamlit Program
# Import all necessary libraries
import argparse
import streamlit as st
import requests
import pandas as pd
from fuzzywuzzy import process, fuzz
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Enter the API key
api_key = "AIzaSyAl6BGuifC0Egek2f4tPPXvjE5BJ2m3r3Y"
# Function to fetch book information from the Google Books API
def fetch_book_info(api_key, book_title, book_author=None):
    query = f'intitle:"{book_title}"'
    api_key = "AIzaSyAl6BGuifC0Egek2f4tPPXvjE5BJ2m3r3Y"
    if book_author and book_author.lower() != 'no':
        query += f'+inauthor:"{book_author}"'
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if not items:
            return None
        book_info = items[0].get('volumeInfo', {})
        return {
            "Title": book_info.get("title", "Unknown"),
            "Author": ', '.join(book_info.get("authors", ["Unknown"])),
            "Categories": ', '.join(book_info.get("categories", ["Unknown"])),
            "PublishedDate": book_info.get("publishedDate", "Unknown"),
            "PageCount": book_info.get("pageCount", "Unknown"),
            "Language": book_info.get("language", "Unknown"),
            "AverageRating": book_info.get("averageRating", "Unknown"),
            "RatingsCount": book_info.get("ratingsCount", "Unknown"),
            "Thumbnail": book_info.get("imageLinks", {}).get("thumbnail", "No image available"),
        }
    else:
        return None

# Function to analyze user preferences from a CSV file
def analyze_user_preferences(df):
    common_genres = df['Categories'].value_counts().index.tolist()
    common_authors = df['Author'].value_counts().index.tolist()

    def select_keywords_from_titles(titles):
        filter_words = {"das", "der", "die", "ein", "eine", "the", "a", "mein", "dein", "sein", "ihr", "wir", "sie"}
        keywords = set()
        for title in titles:
            title_keywords = {word for word in title.split() if word.istitle() and word.lower() not in filter_words}
            keywords.update(title_keywords)
        return list(keywords)

    title_keywords = select_keywords_from_titles(df['Title'])

    return common_genres, common_authors, title_keywords

# Function to determine if a book is already entered based on a fuzzy matching score
def is_book_already_entered(user_book_titles, candidate_title, threshold=90):
    highest_match_score = process.extractOne(candidate_title, user_book_titles, scorer=fuzz.partial_ratio)[1]
    return highest_match_score > threshold

# Function to find similar books based on genres, authors, and keywords
def find_similar_books(genres, authors, title_keywords, user_books, api_key):
    similar_books = []  # This will be a list of dictionaries
    api_key = "AIzaSyAl6BGuifC0Egek2f4tPPXvjE5BJ2m3r3Y"
    for genre in genres:
        for author in authors:
            for keyword in title_keywords:
                query = f"+subject:'{genre}'+inauthor:'{author}'+intitle:'{keyword}'"
                query = query.strip('+')
                url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}&maxResults=40"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        book_info = item.get('volumeInfo', {})
                        book_title = book_info.get('title', "Unknown").lower()
                        # Use fuzzy matching to check if the book is already entered by the user
                        if not is_book_already_entered(user_books, book_title, threshold=90):
                            # Ensure each book is a dictionary with a 'Title' before appending

                            existing_titles = [book['Title'].lower() for book in similar_books]
                            if not existing_titles or not is_book_already_entered(existing_titles, book_title, threshold=90):
                                similar_books.append({
                                    "Title": book_info.get('title', "Unknown"),
                                    "Author": ', '.join(book_info.get("authors", ["Unknown"])),
                                    "Categories": ', '.join(book_info.get("categories", ["Unknown"])),
                                    "PublishedDate": book_info.get("publishedDate", "Unknown"),
                                    "PageCount": book_info.get("pageCount", "Unknown"),
                                    "Language": book_info.get("language", "Unknown"),
                                    "AverageRating": book_info.get("averageRating", "Unknown"),
                                    "RatingsCount": book_info.get("ratingsCount", "Unknown"),
                                    "Thumbnail": book_info.get("imageLinks", {}).get("thumbnail", "No image available"),
                                    "Description": book_info.get("description", "No description available"),
                                    "InfoLink": book_info.get("infoLink", "No link available")
                                })
    return pd.DataFrame(similar_books)



def display_recommendations(df):
    if not df.empty:
        st.write("Top Recommended Books Based on Your Preferences:")
        for _, row in df.iterrows():
            col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed
            with col1:  # Column for the book thumbnail
                st.image(row['Thumbnail'], use_column_width=True)
            with col2:  # Column for the book details
                st.write(f"**{row['Title']}**")
                st.write(f"Author: {row['Author']}")
                st.write(f"Published Date: {row['PublishedDate']}")
                st.write(f"Page Count: {row['PageCount']}")
                st.write(f"Language: {row['Language']}")
                st.write(f"Average Rating: {row['AverageRating']}")
                st.write(f"Ratings Count: {row['RatingsCount']}")
                st.write(row['Description'])
                st.markdown(f"[More Info]({row['InfoLink']})", unsafe_allow_html=True)


# Function for the Homepage of our application
def introduction_to_project():

    st.markdown("""
    <style>
        .background-image-area {
            height: 200px;
            background-image: url('https://learn.podium.school/wp-content/uploads/2023/11/image-188.jpeg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="background-image-area"></div>', unsafe_allow_html=True)

    def display_greeting():
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning"
        elif 12 <= current_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        st.markdown(f"<h1 style='text-align: center;'>{greeting}! Welcome to Bookly</h1>", unsafe_allow_html=True)

    display_greeting()

    st.write("<p style='text-align: center;'>The only site where you can get personalized book recommendations based on your own interests and experience.</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Our Mission")
    st.markdown(""" At Bookly, our mission is to enhance your reading experience:
    - **Personalized Recommendations:** Books tailored to your tastes based on your reading history.
    - **Advanced Analytics:** Data-driven insights to predict books you'll enjoy.
    - **Community of Readers:** A network connecting readers, critics, and lifelong learners.
    - **Local Book Culture Support:** Collaborations with bookstores and literary events.
    - **Literary Discovery:** Embark on a journey to find your next favorite book.
    """)
    st.markdown("---")
    st.image("https://images.deccanherald.com/deccanherald/2023-09/d8399b02-00dc-42b4-b273-0ecfd6161d11/file7s2d5l7d2wo1f4u3j94j.jpg?w=1200&h=675&auto=format%2Ccompress&fit=max&enlarge=true")
    st.markdown("---")
    st.subheader("What do we offer?")
    st.write("Our system can not only give you a wide array of recommendations for your future readings but also analyze your overall reading experience as a part of our community. Furthermore you get the possibility to trade books with other users through our brand new marketplace.")
    with st.expander("Features of Our Platform"):
        st.write("""
        - **Home**: Find out everything about our vision. 
        - **Book Recommendations**: Get personalized book suggestions.
        - **Data Analysis**: Dive deep into the insights of data.
        - **Marketplace**: Explore books available for exchange or purchase.
    """)
    st.markdown("---")
    st.subheader("Where does this project have its origins?")
    st.markdown("Bookly was created by students in order to accomplish a project at the University of St.Gallen. The course Computer Science is a mandatory course in the Bachelors degree in Business Adminstration and challenges individual students to learn about the most important features of programming in an variety of ways.")
    st.markdown("The School of Computer Science is rather new at the University of St.Gallen. If you're eager to learn more about the school check out the video below and dive into the world of programming and machine learning.")
    st.video("https://www.youtube.com/watch?v=_B60aTHCE5E")

# Function for our book recomendation system
def display_book_recommendations():

    st.markdown("""
    <style>
        .background-image-area {
            height: 200px;
            background-image: url('https://learn.podium.school/wp-content/uploads/2023/11/image-188.jpeg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="background-image-area"></div>', unsafe_allow_html=True)

    st.title("Book Information and Recommendation System")
    st.subheader("Ready to dive into a new reading experience?")

    st.markdown("---")
    st.markdown("**How does the book recommendation system work?**")
    st.write("Our cutting edge recommendation system is not only based on your previous book readings but also uses a complex rating system which uses your own experience in providing the optimal book recomendations.")
    st.markdown("---")

    st.subheader("Step #1 Previous Experience")
    st.write("Enter the title and author of the books you have already read.")
    book_title = st.text_input("Book Title")
    book_author = st.text_input("Book Author (leave empty if unknown)")
    st.write("Please press 'Fetch Book Information' after you have entered the details for one book. Once you did so the book has been saved and you can just enter a new one in the same text field. You can enter up to 5 books.")

    if st.button("Fetch Book Information"):
        if book_title == "" and book_author == "":
            st.warning("You must enter a book title or author first")
        elif book_title != "" or book_author != "":
            book_info = fetch_book_info(api_key, book_title, book_author)
            if book_info:

                # Update the session state DataFrame
                if 'book_info_df' not in st.session_state or st.session_state['book_info_df'].empty:
                    st.session_state['book_info_df'] = pd.DataFrame([book_info])
                else:
                    st.session_state['book_info_df'] = st.session_state['book_info_df'].append(book_info, ignore_index=True)

                # Write the session state DataFrame to CSV
                csv_filename = 'book_info.csv'
                st.session_state['book_info_df'].to_csv(csv_filename, index=False)
                st.success(f"Book information saved to {csv_filename}")

                st.write("Entire CSV:")
                st.write(pd.read_csv(csv_filename))


    st.markdown("---")

    st.subheader("Step #2 Claim your future readings")


    # Initialize the session state
    if 'recommendations_df' not in st.session_state:
        st.session_state['recommendations_df'] = None

    if st.button("Get Book Recommendations"):
        if 'book_info_df' in st.session_state and not st.session_state['book_info_df'].empty:
            st.write(analyze_user_preferences(st.session_state['book_info_df']))
            recommendations_df = find_similar_books(*analyze_user_preferences(st.session_state['book_info_df']),
                                                    st.session_state['book_info_df']['Title'].tolist(),
                                                    api_key)
            if not recommendations_df.empty:
                st.write("Top 3 Recommended Books Based on Your Preferences:")
                # Display top 3 recommendations
                for _, row in recommendations_df.head(3).iterrows():
                    col1, col2, col3 = st.columns([1, 3, 1])  # Adjust the ratio as needed
                    with col1:  # Column for the book thumbnail
                        if row['Thumbnail'] and row['Thumbnail'] != "No image available":
                            st.image(row['Thumbnail'], use_column_width=True)
                        else:
                            # Display a placeholder image
                            st.image("https://via.placeholder.com/150?text=No+Image", use_column_width=True)
                    with col2:  # Column for the book description and link
                        st.write(f"**{row['Title']}**")
                        st.write(f"Author: {row['Author']}")
                        st.write(f"Published Date: {row['PublishedDate']}")
                        st.write(f"Page Count: {row['PageCount']}")
                        st.write(f"Language: {row['Language']}")
                        st.write(f"Average Rating: {row['AverageRating']}")
                        st.write(f"Ratings Count: {row['RatingsCount']}")
                        st.write(row['Description'])
                        st.markdown(f"[More Info]({row['InfoLink']})", unsafe_allow_html=True)

                recommendations_df.to_csv('recommended_books.csv', index=False)
                st.success("Recommendations saved to recommended_books.csv")

                # Store recommendations_df in session state
                st.session_state['recommendations_df'] = recommendations_df
            else:
                st.warning("No recommendations found based on your preferences.")
        else:
            st.error("No book information found. Please add some books and fetch their information first.")
    
    
    st.write("Satisfied with your recommendations?")
    st.write("If not,  press 'More Recommendations' or go back to the beginning and add some additional books")
    st.markdown("---")

    if st.button("More Recommendations"):
        if st.session_state['recommendations_df'] is not None:  # Check if recommendations_df has been initialized
            for _, row in st.session_state['recommendations_df'].iloc[3:6].iterrows():
                col1, col2, col3 = st.columns([1, 3, 1])  # Adjust the ratio as needed
                with col1:  # Column for the book thumbnail
                    if row['Thumbnail'] and row['Thumbnail'] != "No image available":
                        st.image(row['Thumbnail'], use_column_width=True)
                    else:
                        # Display a placeholder image
                        st.image("https://via.placeholder.com/150?text=No+Image", use_column_width=True)
                with col2:  # Column for the book description and link
                    st.write(f"**{row['Title']}**")
                    st.write(f"Author: {row['Author']}")
                    st.write(f"Published Date: {row['PublishedDate']}")
                    st.write(f"Page Count: {row['PageCount']}")
                    st.write(f"Language: {row['Language']}")
                    st.write(f"Average Rating: {row['AverageRating']}")
                    st.write(f"Ratings Count: {row['RatingsCount']}")
                    st.write(row['Description'])
                    st.markdown(f"[More Info]({row['InfoLink']})", unsafe_allow_html=True)

        else:
            st.warning("No recommendations available.")


# Function to display our Data Analysis page with different graphs
def display_data_analysis_matplotlib(df):
    if df.empty:
        st.write("No data available for analysis.")
        return
    
    #st.image("https://online.york.ac.uk/wp-content/uploads/2021/07/man-in-a-suit-standing-behind-a-hologram-of-data-analytics.jpg")

    # Categories distribution
    st.markdown("**Distribution of Categories**")
    st.markdown("Here you are able to see the categories you relate to the most.")
    category_counts = df['Categories'].value_counts()
    plt.figure(figsize=(8, 8))  # Adjust the figure size as needed for a pie chart
    plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.axis('equal')
    ax = plt.gca()
    ax.set_facecolor("#FCFBF4")
    st.pyplot(plt)
    plt.clf()

    # Authors distribution
    st.markdown("**Distribution of Authors**")
    st.markdown("Here you are able to see the authors you relate to the most.")
    author_counts = df['Author'].value_counts().head(10)  # Show top 10 authors
    plt.figure(figsize=(10, 4))
    author_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Most Common Authors')
    plt.xlabel('Author')
    plt.ylabel('Frequency')
    ax = plt.gca()
    ax.set_facecolor("#FCFBF4")
    st.pyplot(plt)
    plt.clf()

# Make the function only appear if the needed arguments are given in the book recommendation part.
def display_data_analysis():
    st.title("Analysis of your personal book preferences")
    st.markdown("On this subpage, you can learn more about your personal preferences. The following statistics are based on your input in the Book Recommendation section and can be helpful when browsing for new book on the Marketplace.")
    if 'book_info_df' in st.session_state:
        display_data_analysis_matplotlib(st.session_state['book_info_df'])
    else:
        st.error("No book information found. Please enter some book information in the 'Book Recommendations' section first.")
    

# Building the marketplace

# Initialize the marketplace DataFrame
data = {
    'Title': {
        0: 'Das kommunistische Manifest',
        1: 'Das St. Galler Management-Modell',
        2: 'Learn Coding with Python',
        3: 'Faust'
    },
    'Author': {
        0: 'Karl Marx',
        1: 'Johannes Rüegg-Stürm, Simon Grand',
        2: 'Martin Delaney',
        3: 'Johann Wolfgang von Goethe'
    },
    'Categories': {
        0: 'Philosophy',
        1: 'Business & Economics',
        2: 'Computers',
        3: 'Unknown'
    },
    'PageCount': {
        0: 95,
        1: 290,
        2: 87,
        3: 48
    },
    'Language': {
        0: 'de',
        1: 'de',
        2: 'en',
        3: 'de'
    },
    'Thumbnail': {
        0: 'http://books.google.com/books/content?id=AKZpEAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api',
        1: 'http://books.google.com/books/content?id=QBizDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api',
        2: 'http://books.google.com/books/content?id=c9eREAAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api',
        3: 'http://books.google.com/books/content?id=aTZBAAAAcAAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'
    },
    'Email': {
        0: 'karl.marx@unisg.ch',
        1: 'thomas.bieger@unisg.ch',
        2: 'CodingIstCool@unisg.ch',  
        3: 'SchillerIstBesser@unisg.ch'   
    }}  # Random emails

def display_marketplace_data_analysis():
    st.title("Analysis of the marketplace entries")
    st.markdown("On this subpage, you can learn more about the kind of books and authors that you can find in the marketplace.")

    
    display_data_analysis_matplotlib(pd.DataFrame(data))

if 'marketplace_df' not in st.session_state:
    st.session_state['marketplace_df'] = pd.DataFrame(data)

# Display the marketplace
def display_marketplace():
    st.title("Welcome to the Marketplace")
    st.write("**Here you can see the current book offerings.**")
    if not st.session_state['marketplace_df'].empty:
        for _, row in st.session_state['marketplace_df'].head(10).iterrows():
            col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed
            with col1:  # Column for the book thumbnail
                st.image(row['Thumbnail'], use_column_width=True)
            with col2:  # Column for the book description and link
                st.write(f"**{row['Title']}**")
                st.write(f"Author: {row['Author']}")
                st.write(f"Page Count: {row['PageCount']}")
                st.write(f"Language: {row['Language']}")
                st.write("Contact Email:", row['Email'])


    st.subheader("Browse the Marketplace")
    search_query = st.text_input("Search for books by title or author")

    results = st.session_state.marketplace_df[
        st.session_state.marketplace_df['Title'].str.contains(search_query, case=False, na=False) |
        st.session_state.marketplace_df['Author'].str.contains(search_query, case=False, na=False)
        ] if search_query else st.session_state.marketplace_df

    if not results.empty:
        for _, row in results.iterrows():
            with st.expander(f"{row['Title']} by {row['Author']}"):
                if row.get('Thumbnail', ''):
                    st.image(row['Thumbnail'], use_column_width=True)
                st.write(f"Author: {row['Author']}")
                st.write(f"Page Count: {row['PageCount']}")
                st.markdown(f"**Language:** {row['Language']}")
                st.markdown(f"**Email:** {row['Email']}")
                if row.get('Link', ''):
                    st.markdown(f"[More Info]({row['Link']})", unsafe_allow_html=True)
    else:
        st.write("This book or author was not found in the marketplace. Perhaps writing the name in a shorter version helps.")

def add_book_to_marketplace(api_key="AIzaSyAl6BGuifC0Egek2f4tPPXvjE5BJ2m3r3Y"):
    st.subheader("Add a Book to the Marketplace")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    email = st.text_input("Your Email")

    fetch_details = st.button("Fetch Book Details")

    if fetch_details:
        book_info = fetch_book_info(api_key, title, author)
        if book_info:
            st.session_state['book_details'] = book_info  # Store fetched details in session state
            st.success("Book details fetched successfully!")
            thumbnail_url = book_info.get('Thumbnail', 'https://via.placeholder.com/150?text=No+Image')
            st.image(thumbnail_url, use_column_width=True)
            st.write(f"**Title:** {book_info.get('Title', 'Unknown')}")
            st.write(f"**Author:** {(book_info.get('Authors', ['Unknown']))}")
            st.write(f"**Categories:** {(book_info.get('Categories', ['Unknown']))}")
        else:
            st.error("Failed to fetch book details. Please check the inputs and try again.")

    if 'book_details' in st.session_state:
        confirm = st.button("Yes, this is the correct book, add it to the marketplace")
        if confirm:
            new_entry = {
                'Title': st.session_state['book_details']['Title'],
                'Author': (st.session_state['book_details']['Author']),
                'Language': st.session_state['book_details'].get('Language', 'Unknown'),
                'Email': email,
                'Link': st.session_state['book_details'].get('InfoLink', ''),
                'Thumbnail': st.session_state['book_details'].get('Thumbnail', 'https://via.placeholder.com/150')  # Use stored thumbnail
            }
            # Append the new entry to the DataFrame in session_state
            st.session_state.marketplace_df = st.session_state.marketplace_df.append(new_entry, ignore_index=True)
            st.success("Your book has been added to the marketplace!")
            st.experimental_rerun()
            # Clear the book details and confirmation flag from session state
            del st.session_state['book_details']
            del st.session_state['confirmed']


# Streamlits main function
def main():

    if 'section' not in st.session_state:
        st.session_state['section'] = 'Home'

    # Sidebar navigation
    if st.sidebar.button('Home'):
        st.session_state['section'] = 'Home'
    if st.sidebar.button("Book Recommendations"):   
        st.session_state['section'] = 'Book Recommendations'
    if st.sidebar.button('Data Analysis'):
        st.session_state['section'] = 'Data Analysis'
    if st.sidebar.button('Marketplace'):
        st.session_state['section'] = 'Marketplace'

    # Display the section based on the current state
    if st.session_state['section'] == 'Home':
        introduction_to_project()
    elif st.session_state['section'] == 'Book Recommendations':
        display_book_recommendations()
    elif st.session_state['section'] == 'Data Analysis':
        st.title("Data Analysis")
        with st.expander("Marketplace Data Analysis"):
             display_marketplace_data_analysis()
        with st.expander("Personal Preference Data Analysis"):
            display_data_analysis()
    elif st.session_state['section'] == 'Marketplace':
        display_marketplace()
        add_book_to_marketplace()

if __name__ == "__main__":
    main()

#%%
