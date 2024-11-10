# CityReads - Local Book Recommendation Engine based on Users Interest

## Problem Statement

Welcome to an innovative digital library platform that revolutionizes the way individuals connect with knowledge and stories in the digital age. Our mission is to create a user-centric experience that empowers users to explore, discover, and engage with content tailored to their unique interests and preferences.

In response to the limitations of traditional library interfaces, our platform aims to address the challenges users face in finding content that resonates with them. By harnessing the power of advanced technologies and data-driven methodologies, we will introduce personalized recommendations, interactive features, and immersive audio trailers to enhance the overall user experience.

Our platform will offer personalized book recommendations based on users' reading history and preferences, enhancing engagement and satisfaction. Additionally, users can enjoy audio trailers for recommended books, providing captivating previews of the content using AI-driven text-to-speech synthesis. These features aim to help users make informed decisions and connect with stories on a deeper level.

At the core of our efforts are the end users: library patrons seeking a more intuitive and enriching digital library experience.

Through personalized book recommendations and immersive audio trailers, our platform will provide users with a tailored and engaging experience. By integrating machine learning algorithms and AI-driven text-to-speech synthesis, we will create a dynamic library platform that empowers users to discover, explore, and connect with content in meaningful ways.

Our focus is on enhancing user satisfaction, facilitating informed decision-making, and fostering a vibrant community of readers. We invite stakeholders to join us on this journey as we shape the future of digital libraries and inspire a love of learning and storytelling.



## Architecture Diagram
![326124979-a50711ae-f3d1-486a-9812-526c7925966a](https://github.com/user-attachments/assets/0770d9fb-2ddf-4094-863a-91a6c4eb655d)

## Technology Stack
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=purple)](https://www.python.org/)
[![Apache Airflow](https://img.shields.io/badge/apacheairflow-2A667F?style=for-the-badge&logo=ApacheAirflow&logoColor=black)](https://airflow.apache.org/)
[![Pinecone](https://img.shields.io/badge/Pinecone-A100FF?style=for-the-badge)](https://www.pinecone.io/)
[![OpenAI Clip](https://img.shields.io/badge/openai-6BA539?style=for-the-badge&logo=OpenAI&logoColor=black)](https://openai.com/)
[![Docker](https://img.shields.io/badge/docker-29F1FB?style=for-the-badge&logo=Docker&logoColor=black)](https://www.docker.com/)
[![Amazon S3](https://img.shields.io/badge/amazons3-535D6C?style=for-the-badge&logo=amazons3&logoColor=black)](https://aws.amazon.com/s3/)


## Setup 
### Pre-requisite
  - Local: Windows 11, Docker (WLS 2), Python, Streamlit
  - Cloud: PineCone Vector Database Account, AWS S3, Snowflake Account
## Setup 
On local machine, open command prompt
python -m venv .venv


## Using the Application
- User Registration and Login:
  - As a new user, navigate to the sign-up page to register.
  - Provide necessary details and register.
  - Log in using your credentials.
  - Existing users can log in directly using their credentials.
  - New users are greeted by a chatbot.
  - Answer questions about preferred types of books, mood, theme, and pace.
  - Go to Book Recommendation tab on the Navigation bar to get initial book recommendations based on your answers.
  

![325804363-22d3f1c0-a6a4-4611-af6d-0561402a9ca0](https://github.com/user-attachments/assets/9b51bd32-1280-42a7-995a-c76df7e04d39)

- Searching for Books:
  - Go to the Search Books Tab.
  - Search title of the book you want to see
  - Results are displayed, which you can add to "Started Reading," "To Be Read," or "Read" lists.
  
![image](https://github.com/BigDataIA-Spring2024-Sec1-Team4/FinalProject/assets/114356265/50bfd72a-ff46-4d9a-af3c-a56a116b95fc)

- User Dashboard:
  - View the books you have added in different categories.
  - Rate books you've read on a scale of 1 to 5.

![image](https://github.com/BigDataIA-Spring2024-Sec1-Team4/FinalProject/assets/114356265/7c7aa84a-07a5-4283-b688-a2b99c9ec1a2)


- Refreshing Recommendations:
  - Navigate to the Book Recommendation Tab.
  - Click on Refresh Recommendation to receive new suggestions based on your reading history and reviews.
  
![image](https://github.com/BigDataIA-Spring2024-Sec1-Team4/FinalProject/assets/114356265/a5c3b39e-9cdb-48fd-a799-b9e0a47c3845)

## Project Structure:

```
├── Makefile
├── airflow
│   ├── config
│   ├── dags
│   │   ├── __pycache__
│   │   │   └── run.cpython-312.pyc
│   │   ├── run.py
│   │   └── scripts
│   │       ├── audio_linkgeneration.py
│   │       ├── audio_processing.py
│   │       ├── getSeattleLibrary.py
│   │       └── inventory_preprocessing.py
│   ├── logs
│   │   ├── dag_processor_manager
│   │   │   └── dag_processor_manager.log
│   │   └── scheduler
│   │       ├── 2024-04-25
│   │       │   └── run.py.log
│   │       └── latest -> 2024-04-25
│   └── plugins
├── backend
│   ├── Dockerfile
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── get_book_details.cpython-39.pyc
│   │   ├── main.cpython-310.pyc
│   │   ├── main.cpython-311.pyc
│   │   └── main.cpython-39.pyc
│   ├── main.py
│   ├── requirements.txt
│   └── utils
│       ├── __pycache__
│       │   ├── login_backend.cpython-310.pyc
│       │   ├── login_backend.cpython-311.pyc
│       │   ├── login_backend.cpython-39.pyc
│       │   ├── snowflake_connector.cpython-310.pyc
│       │   ├── snowflake_connector.cpython-311.pyc
│       │   └── snowflake_connector.cpython-39.pyc
│       ├── login_backend.py
│       └── snowflake_connector.py
├── docker-compose.yaml
├── requirements.txt
├── scripts
│   ├── DataPreprocessing
│   │   ├── Goodreads_Preprocessing.py
│   │   ├── Goodreads_Preprocessing_2.py
│   │   └── getBookInventory.py
│   ├── GoodreadsScraper
│   │   ├── CSV
│   │   │   ├── goodreads_merged.csv
│   │   │   ├── out_books.csv
│   │   │   ├── out_decade_books.csv
│   │   │   ├── out_mystrey_books.csv
│   │   │   ├── out_once_books.csv
│   │   │   └── out_young_books.csv
│   │   ├── GoodreadsScraper
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── __init__.cpython-310.pyc
│   │   │   │   ├── items.cpython-310.pyc
│   │   │   │   ├── pipelines.cpython-310.pyc
│   │   │   │   └── settings.cpython-310.pyc
│   │   │   ├── custom_filters.py
│   │   │   ├── items.py
│   │   │   ├── middlewares.py
│   │   │   ├── pipelines.py
│   │   │   ├── settings.py
│   │   │   └── spiders
│   │   │       ├── __init__.py
│   │   │       ├── __pycache__
│   │   │       │   ├── __init__.cpython-310.pyc
│   │   │       │   ├── author_spider.cpython-310.pyc
│   │   │       │   ├── book_spider.cpython-310.pyc
│   │   │       │   ├── list_spider.cpython-310.pyc
│   │   │       │   └── mybooks_spider.cpython-310.pyc
│   │   │       ├── author_spider.py
│   │   │       ├── book_spider.py
│   │   │       └── list_spider.py
│   │   ├── book_goodreads_book.jl
│   │   ├── book_goodreads_decade_book.jl
│   │   ├── book_goodreads_mystrey_book.jl
│   │   ├── book_goodreads_once_book.jl
│   │   ├── book_goodreads_young_book.jl
│   │   ├── chromedriver
│   │   ├── cleanup.py
│   │   ├── crawl.py
│   │   ├── merge.py
│   │   ├── scrapy.cfg
│   │   └── scrapy.log
│   ├── book_attributes.csv
│   ├── book_attributes_null.csv
│   ├── csv_snowflake.py
│   ├── getBookProfile.py
│   └── openai_newkey.py
└── streamlit
    ├── Dockerfile
    ├── __pycache__
    │   ├── book_recommendation.cpython-310.pyc
    │   ├── book_recommendation.cpython-311.pyc
    │   ├── book_recommendation.cpython-39.pyc
    │   ├── search_book.cpython-310.pyc
    │   ├── search_book.cpython-311.pyc
    │   ├── search_book.cpython-39.pyc
    │   ├── search_book_new.cpython-310.pyc
    │   ├── search_book_new.cpython-311.pyc
    │   ├── search_book_new.cpython-39.pyc
    │   ├── user_dashboard.cpython-310.pyc
    │   ├── user_dashboard.cpython-311.pyc
    │   ├── user_dashboard.cpython-39.pyc
    │   ├── user_survey.cpython-310.pyc
    │   ├── user_survey.cpython-311.pyc
    │   └── user_survey.cpython-39.pyc
    ├── book_recommendation.py
    ├── login.py
    ├── main.py
    ├── pages
    ├── requirements.txt
    ├── search_book.py
    ├── search_book_new.py
    ├── streamlit_app.py
    ├── user_dashboard.py
    ├── user_survey.py
    └── utils
        ├── __pycache__
        │   ├── book_details.cpython-310.pyc
        │   ├── book_details.cpython-311.pyc
        │   └── book_details.cpython-39.pyc
        ├── book_details.py
        └── get_user_profile.py
```

## References:
- ChatGPT: https://chat.openai.com/
- OpenAI CLIP: https://towardsdatascience.com/quick-fire-guide-to-multi-modal-ml-with-openais-clip-2dad7e398ac0 
- Fast API: https://fastapi.tiangolo.com/
- Airflow: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
- Pinecone: https://www.pinecone.io/learn/vector-database/
- Docker: https://www.docker.com/#
- JWT Tokens: https://jwt.io/introduction
- gTTs: https://gtts.readthedocs.io/en/latest/

