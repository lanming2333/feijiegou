from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)  # Allows CORS for all domains

# Load data
df = pd.read_csv('D:\code\非结构化数据分析\cleaned_data_pro.csv', encoding='utf-8')
relevant_columns = ['cuisines', 'top_tags', 'price_level', 'meals', 'avg_rating', 'original_location', 'address', 'awards', 'special_diets', 'features']
df['mixed_features'] = df[relevant_columns].apply(lambda row: " ".join(row.values.astype(str)), axis=1)
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['mixed_features'])

@app.route('/search', methods=['POST'])
def search():
    user_input = request.json.get('query')
    user_input_tfidf = tfidf_vectorizer.transform([user_input])
    cosine_similarities = cosine_similarity(user_input_tfidf, tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-5:][::-1]
    results = [
        {
            'score': float(cosine_similarities[i]),
            'name': df.iloc[i]['restaurant_name'],
            'index': int(df.index[i])
        } for i in similar_indices
    ]
    return jsonify(results)

@app.route('/details/<int:index>', methods=['GET'])
def details(index):
    selected_restaurant = df.loc[index]
    details = {  # Convert all potentially problematic types
        "Name": str(selected_restaurant['restaurant_name']),
        "Location": str(selected_restaurant['original_location']),
        "Country": str(selected_restaurant.get('country', '')),
        "Region": str(selected_restaurant.get('region', '')),
        "Province": str(selected_restaurant.get('province', '')),
        "City": str(selected_restaurant['city']),
        "Address": str(selected_restaurant['address']),
        "Latitude": float(selected_restaurant['latitude']),
        "Longitude": float(selected_restaurant['longitude']),
        "Awards": str(selected_restaurant['awards']),
        "Popularity": str(selected_restaurant.get('popularity_generic', '')),
        "TopTags": str(selected_restaurant['top_tags']),
        "PriceLevel": str(selected_restaurant['price_level']),
        "Meals": str(selected_restaurant['meals']),
        "Cuisines": str(selected_restaurant['cuisines']),
        "SpecialDiets": str(selected_restaurant['special_diets']),
        "Features": str(selected_restaurant['features']),
        "VegetarianFriendly": str(selected_restaurant.get('vegetarian_friendly', '')),
        "VeganOptions": str(selected_restaurant.get('vegan_options', '')),
        "GlutenFree": str(selected_restaurant.get('gluten_free', '')),
        "AverageRating": float(selected_restaurant['avg_rating']),
        "TotalReviewCount": int(selected_restaurant['total_reviews_count']),
        "ReviewCountInDefaultLanguage": int(selected_restaurant.get('reviews_count_in_default_language', '0')),
        "Excellent": int(selected_restaurant['excellent']),
        "VeryGood": int(selected_restaurant['very_good']),
        "Average": int(selected_restaurant['average']),
        "Poor": int(selected_restaurant['poor']),
        "Terrible": int(selected_restaurant['terrible']),
        "Food": float(selected_restaurant['food']),
        "Service": float(selected_restaurant['service']),
        "Value": float(selected_restaurant['value']),
        "Atmosphere": float(selected_restaurant['atmosphere'])
    }

    # Calculate similarities
    cosine_similarities = cosine_similarity(tfidf_matrix[index:index + 1], tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-6:][::-1]
    recommendations = [
        {
            'score': float(cosine_similarities[i]),
            'name': df['restaurant_name'][i],
            'index': int(i)
        } for i in similar_indices if i != index
    ]

    return jsonify({"details": details, "recommendations": recommendations})

if __name__ == '__main__':
    app.run(debug=True)


