
def hash_function_1(value, a, b, prime_number):
    ''' This is a hash function based on the division-remainder method
    (mapping a key k into a slot m by taking the remainder of k divided by a number p)
    It takes four parameters: a value to be hashed, a, b and a prime number, and
    calculates the hash value of a given value.
    '''
    return (a * value + b) % prime_number


def minhash_signature(values, num_hashes):
    ''' This function inplements minhashing from scratch. It takes a value
    and a number as parameters and calculates the minhashed value (a.k.a signature)
    of the input value by applying a predefined hash function 'num_hashes' # of times.
    '''
    import random
    from random import randint
    from sympy import primerange
    
    # Create a list to store generated signature
    signatures = [float('inf')] * num_hashes

    # Generate random parametes for the defined hash function
    a = [randint(1, 100) for _ in range(num_hashes)]
    b = [randint(1, 100) for _ in range(num_hashes)]
    prime_numbers = list(primerange(700, 900))[:num_hashes]

    # Apply 'number_hashes' # of randomly genrerated hash functions in each loop iteration
    for row_index, value in enumerate(values):
        
        # Only apply hash function to the index of the genres exist in user (value) genres column
        if value == 1:
            
            # Compute hash values for each hash function
            hash_values = [hash_function_1(row_index, a_i, b_i, prime_number) for a_i, b_i, prime_number in zip(a, b, prime_numbers)]

            # Calculate minhash signatures by choosing the minimum hashed value
            for sig_index in range(num_hashes):
                signatures[sig_index] = min(signatures[sig_index], hash_values[sig_index])

    return signatures


def hash_function_2(value, a, b, prime_number):
    ''' This is a hash function based on the division-remainder method.
    It takes four parameters: a value to be hashed, a, b and a prime number, and
    returns the MINIMUM hashed value of a given value.
    '''
    return min((a * val + b) % prime_number for val in value)


def create_buckets(signature, num_rows):
    ''' This function takes a signature and a number as parameters.
    It uses num_rows for choosing a group of rows and calculates the hashed value of
    them representing their bucket number.
    '''
    # Create a list to store hash values for each band
    hash_table = []
    # Define hash function parameters
    a,b = 30,17
    prime_number = 521

    # Iterate over each band
    for band_index in range(len(signature)//num_rows):

        # Extract the signature for the current band
        band_signature = signature[band_index*num_rows:band_index*num_rows + num_rows]

        # Calculate a hash value for these signature which actually maps the signature to buckets
        hash_value = hash_function_2(band_signature, a, b, prime_number)

        # Append the corresponding bucket to the hash table list
        hash_table.append(hash_value)

    return hash_table


def compute_jaccard_similarity(user1_bucket, user2_bucket):
    ''' This function takes two users as input and compute
    the Jaccard similarity between them by dividing the size
    of sets of their buckets intersection and union.
    '''    
    # Calculate the size of the intersection and union sets between the given two users
    intersection_size = len(set(user1_bucket).intersection(user2_bucket))
    union_size = len(set(user1_bucket).union(user2_bucket))

    if union_size == 0:
        return 0.0
    # Jaccard similarity of two sets is their intersection divided by their union
    return intersection_size / union_size

def find_similar_users(user_id, buckets, threshold=0.5):
    ''' This function finds similar users to the given
    user id and a set of buckets passed in as a dictionary
    based on a defined threshold.
    '''    
    # Define a set containing all the buckets the user appeared in
    user_bucket = buckets.get(user_id, [])

    if len(user_bucket) == 0:
        print(f"Error: No bucket information available for user {user_id}. Cannot compute similarity.")
        return []
    # Create a list to store similar users
    similar_users = []

    # Iterate over all other users and calculate the similarity between their corresponding buckets and the user_bucket
    for other_user, other_bucket in buckets.items():
        if other_user != user_id:
            # Calling compute_jaccard_similarity function
            similarity = compute_jaccard_similarity(user_bucket, other_bucket)
            if similarity >= threshold:
                similar_users.append((other_user, similarity))
                
    # Sort the list of similar users based on their Jaccard similarity scores in descending order
    similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)

    return similar_users


# Function to recommend movies to a user
def recommend_movies(user_id, similar_users, clicks_df, num_recommendations=5):
    '''This function recommends movies for a given user based on the movies
    clicked (5 most clicked) by similar users. The parameters are user_id,
    buckets which is a dictionary mapping user IDs to their corresponding buckets,
    clicks dataframe containing user clicks data, and num_recommendations for
    the maximum number of movies to recommend (default is 5).
    '''
    # Create a list to store recommended movies
    recommended_movies = []

    # Sort similar users by Jaccard similarity score
    similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)

    # Iterate over similar users
    for similar_user, _ in similar_users:
        # Extract movies clicked by the similar user
        similar_user_movies = clicks_df[clicks_df['user_id'] == similar_user]

        # Check if there are common movies between the current user and similar user
        common_movies = set(similar_user_movies['title']).intersection(recommended_movies)

        # Recommend common movies based on the total number of clicks by both users
        if common_movies:
            common_movies_df = clicks_df[clicks_df['title'].isin(common_movies)]
            common_movies_recommendation = common_movies_df.groupby('title')['click_count'].sum().reset_index()
            common_movies_recommendation = common_movies_recommendation.sort_values(by='click_count', ascending=False)['title'].tolist()
            recommended_movies.extend(common_movies_recommendation)

        # If there are less than 5 common movies, recommend additional movies from the similar user
        if len(recommended_movies) < num_recommendations:
            additional_movies = similar_user_movies.sort_values(by='click_count', ascending=False)['title'].unique()
            additional_movies = [movie for movie in additional_movies if movie not in recommended_movies][:num_recommendations - len(recommended_movies)]
            recommended_movies.extend(additional_movies)

        # Break the loop if we have reached the desired number of recommendations
        if len(recommended_movies) >= num_recommendations:
            break

    return recommended_movies[:num_recommendations]
