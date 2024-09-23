import sqlite3
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from database import DATABASE

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
connct = sqlite3.connect(DATABASE)
query = "SELECT id, title, description FROM courses"
courses_df = pd.read_sql(query, connct)
descriptions = courses_df['description'].tolist()
course_embeddings = model.encode(descriptions)
courses_df['embedding'] = list(course_embeddings)
interaction_query = """
    SELECT course_students.course_id, course_students.student, 1 AS enrolled, 0 AS liked
    FROM course_students
    UNION
    SELECT course_likes.course_id, course_likes.student, 0 AS enrolled, 1 AS liked
    FROM course_likes;
"""
user_course_data = pd.read_sql(interaction_query, connct)
connct.close()


user_course_matrix = user_course_data.pivot_table(index='student', columns='course_id', values=['enrolled', 'liked'], fill_value=0)
user_course_matrix.columns = ['_'.join(map(str, col)) for col in user_course_matrix.columns]
course_similarity_collab = cosine_similarity(user_course_matrix.T)
course_similarity_content = cosine_similarity(course_embeddings)

alpha = 0.5  
combined_similarity = (alpha * course_similarity_collab) + ((1 - alpha) * course_similarity_content)
combined_similarity_df = pd.DataFrame(combined_similarity, index=courses_df['id'], columns=courses_df['id'])

def recommend_courses_with_content(user, num_recommendations=5):
    user_interactions = user_course_matrix.loc[user]
    interacted_courses = user_interactions[user_interactions > 0].index
    
    similarity_scores = combined_similarity_df[interacted_courses].sum(axis=1)
    
    similarity_scores = similarity_scores.drop([int(course.split('_')[1]) for course in interacted_courses])
    
    recommended_courses = similarity_scores.sort_values(ascending=False).head(num_recommendations)
    return recommended_courses

if __name__ == '__main__':
    user = 'student_username'
    recommendations = recommend_courses_with_content(user, num_recommendations=5)

    print("Recommended courses for user:", user)
    print(recommendations)
