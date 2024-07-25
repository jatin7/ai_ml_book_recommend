import streamlit as st
from streamlit.components.v1 import html
from streamlit_chat import message
import pandas as pd
from utils.book_details import matched_books


def chatbot(user_id):
    st.title("Book Recommendation Chatbot")

    message("Hi, To help you find a book, I need some info") 

    # Genre
    message("What genres do you like? ")
    genres = ["Fantasy", "Science Fiction", "Mystery/Thriller/Crime", "Romance", "Horror"]
    selected_genres = st.multiselect("Select genres", genres)
    if selected_genres:
        message(f"I like {', '.join(selected_genres)}!", is_user=True)

        # Mood
        message("What would you like the mood of the book? ")
        selected_mood = st.selectbox( "?",
            ("","Heartfelt", "Inspiring", "Dark and Mysterious", "Thought-Provoking nature", "Contemplative"))
    
        if selected_mood:
            mood_score_mapping = {
                    "Heartfelt": (1,2),
                    "Inspiring": (3,4),
                    "Dark and Mysterious": (5,6),
                    "Thought-Provoking nature": (7,8),
                    "Contemplative": (9,10)
                }
            message(f"I like {(selected_mood)}", is_user=True)
            mood_score = mood_score_mapping[selected_mood]
            mood_score_str = str(mood_score)

          
            # Theme
            message("What Theme do you prefer?")
            theme = ["Justice", "Love", "Redemption", "Courage", "Coming of Age", "Survival", "Identity", "Betrayal", "Sacrifice", "Freedom vs. Oppression"]
            selected_theme = st.multiselect("Select theme", theme)
            theme_score_mapping = {
                                    "Justice": 1,
                                    "Love": 2,
                                    "Redemption": 3,
                                    "Courage": 4,
                                    "Coming of Age": 5,
                                    "Survival": 6,
                                    "Identity": 7,
                                    "Betrayal": 8,
                                    "Sacrifice": 9,
                                    "Freedom vs. Oppression": 10
                                }

            if selected_theme:
                message(f"I like {', '.join(selected_theme)}", is_user=True)
                theme_scores_str = '|'.join(str(theme_score_mapping[theme]) for theme in selected_theme)

                #message(f" {', '.join(selected_theme)} books are the Best!!!")

            # Plot Complexity
                message("How complex do you like the plot to be?")
                plot_complexity = ["Easy", "Medium", "Complex"]
                selected_plot_complexity = st.select_slider("Select plot complexity", plot_complexity)
                plot_score_mapping = {
                                                "Easy": 1,
                                                "Medium": 5,
                                                "Complex": 10
                                            }

                if selected_plot_complexity:
                    plot_score = plot_score_mapping[selected_plot_complexity]
                    message(f"I like {selected_plot_complexity} plot", is_user=True)
                    #message(f"{selected_plot_complexity} plot books are the Best!!!")

                    # Pace
                    message("What pace do you prefer?")
                    pace = ["","Slow", "Medium", "Fast"]
                    pace_score_mapping = {
                                                "Slow": 1,
                                                "Medium": 5,
                                                "Fast": 10
                                            }
                    selected_pace = st.selectbox("Select pace", pace)

                    if selected_pace:
                        pace_score = pace_score_mapping[selected_pace]
                        message(f"I like {(selected_pace)}", is_user=True)
                        #message(f" {(selected_pace)} books are the Best!!!")

                        # Length
                        message("What length of book do you prefer?")
                        length = ["upto 300 pages", "300-500 pages", "500+ pages"]
                        length_score_mapping = {
                                                "upto 300 pages": 1,
                                                "300-500 pages": 5,
                                                "500+ pages": 10
                                            }
                        selected_length = st.select_slider("Select length", length)

                        if selected_length:
                            length_score = length_score_mapping[selected_length]
                            message(f"I like {selected_length}", is_user=True)
   
                            genre = ', '.join(selected_genres)
                            matched_books(user_id,genre,mood_score_str,theme_scores_str,plot_score,pace_score,length_score)
                            #user_id,genre,mood,theme,plot_complexity,pace,length
                        

def main():
    user_data = st.session_state.get('data', None)
    user_id = user_data['u_id']
    chatbot(user_id=user_id)

if __name__ == "__main__":
    main()
