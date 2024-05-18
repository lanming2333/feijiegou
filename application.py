from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import happybase
import subprocess

app = Flask(__name__)
CORS(app)  # Allows CORS for all domains

# Load data
# df = pd.read_csv('/home/hadoop/桌面/cleaned_data_pro.csv', encoding='utf-8')
# relevant_columns = ['cuisines', 'top_tags', 'price_level', 'meals', 'avg_rating', 'original_location', 'address', 'awards', 'special_diets', 'features']

def load_data_from_hbase():
    connection = happybase.Connection('localhost', port=9090)
    table = connection.table('restaurants')  # Assume the table name is 'restaurants'

    # Updated: Include all needed columns from HBase with column family:qualifier format
    columns = [
        'details:restaurant_name', 'details:original_location', 'details:country', 'details:region',
        'details:province', 'details:city', 'details:address', 'details:latitude', 'details:longitude',
        'details:awards', 'details:popularity_generic', 'details:top_tags', 'details:price_level',
        'details:meals', 'details:cuisines', 'details:special_diets', 'details:features',
        'details:vegetarian_friendly', 'details:vegan_options', 'details:gluten_free',
        'details:avg_rating', 'details:total_reviews_count', 'details:default_language',
        'details:reviews_count_in_default_language', 'details:excellent', 'details:very_good',
        'details:average', 'details:poor', 'details:terrible', 'details:food', 'details:service',
        'details:value', 'details:atmosphere'
    ]  # Add or modify according to the actual qualifiers in your HBase table

    rows = []

    for key, data in table.scan(columns=columns):
        print("Read a ROW")
        # 确保只解码和提取实际存在于 'data' 中的列
        row_key = key.decode('utf-8')  # 将二进制的行键解码为字符串
        decoded_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}  # 解码每个列限定符和它们的值
        # row = {column.decode('utf-8').split(':')[1]: data.get(column, b'').decode('utf-8') for column in columns ifcolumn in data}
        rows.append(decoded_data)

    df = pd.DataFrame(rows)
    connection.close()
    return df


# Load data
df = load_data_from_hbase()
print(df.columns)
#relevant_columns = ['cuisines', 'top_tags', 'price_level', 'meals', 'avg_rating', 'original_location', 'address', 'awards', 'special_diets', 'features']

# Define relevant columns for mixed_features calculation
relevant_columns = ['details:cuisines', 'details:top_tags', 'details:price_level', 'details:meals', 'details:avg_rating', 'details:original_location', 'details:address', 'details:awards', 'details:special_diets', 'details:features']

#relevant_columns = ['cuisines', 'top_tags', 'price_level', 'meals', 'avg_rating','original_location', 'address', 'awards', 'special_diets', 'features']

missing_columns = [col for col in relevant_columns if col not in df.columns]
# print("Missing columns:", missing_columns)



df['mixed_features'] = df[relevant_columns].apply(lambda row: " ".join(row.values.astype(str)), axis=1)
#df['mixed_features'] = df[relevant_columns].apply(lambda row: " ".join(row.values.astype(str)), axis=1)
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
            'name': df.iloc[i]['details:restaurant_name'],
            'index': int(df.index[i])
        } for i in similar_indices
    ]
    return jsonify(results)

@app.route('/details/<int:index>', methods=['GET'])
def details(index):
    selected_restaurant = df.loc[index]
    details = {  # Convert all potentially problematic types
        "Name": str(selected_restaurant['details:restaurant_name']),
        "Location": str(selected_restaurant['details:original_location']),
        "Country": str(selected_restaurant.get('details:country', '')),
        "Region": str(selected_restaurant.get('details:region', '')),
        "Province": str(selected_restaurant.get('details:province', '')),
        "City": str(selected_restaurant['details:city']),
        "Address": str(selected_restaurant['details:address']),
        "Latitude": float(selected_restaurant['details:latitude']),
        "Longitude": float(selected_restaurant['details:longitude']),
        "Awards": str(selected_restaurant['details:awards']),
        "Popularity": str(selected_restaurant.get('details:popularity_generic', '')),
        "TopTags": str(selected_restaurant['details:top_tags']),
        "PriceLevel": str(selected_restaurant['details:price_level']),
        "Meals": str(selected_restaurant['details:meals']),
        "Cuisines": str(selected_restaurant['details:cuisines']),
        "SpecialDiets": str(selected_restaurant['details:special_diets']),
        "Features": str(selected_restaurant['details:features']),
        "VegetarianFriendly": str(selected_restaurant.get('details:vegetarian_friendly', '')),
        "VeganOptions": str(selected_restaurant.get('details:vegan_options', '')),
        "GlutenFree": str(selected_restaurant.get('details:gluten_free', '')),
        "AverageRating": float(selected_restaurant['details:avg_rating']),
        "TotalReviewCount": int(float(selected_restaurant['details:total_reviews_count'])),
        # "TotalReviewCount": int(selected_restaurant['details:total_reviews_count']),
        "ReviewCountInDefaultLanguage": int(float(selected_restaurant.get('details:reviews_count_in_default_language', '0'))),
        # "ReviewCountInDefaultLanguage": int(selected_restaurant.get('details:reviews_count_in_default_language', '0'))
    }

    # Calculate similarities
    cosine_similarities = cosine_similarity(tfidf_matrix[index:index + 1], tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-6:][::-1]
    recommendations = [
        {
            'score': float(cosine_similarities[i]),
            'name': df['details:restaurant_name'][i],
            'index': int(i)
        } for i in similar_indices if i != index
    ]

    return jsonify({"details": details, "recommendations": recommendations})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, use_reloader=False)

