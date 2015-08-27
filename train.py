import re

from tinydb import TinyDB
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib

# Load training data
db = TinyDB('reddit.json')
posts_db = db.table('reddit')
all_posts = posts_db.all()
df = pd.DataFrame(all_posts)

# Get rid of all the junk. Keep ASCII alphabets only.
# TODO: Fix to support non-English languages.
regex = re.compile('[^a-zA-Z ]')
cleaned_df = df['text'].map(lambda x: ' '.join(regex.sub('', x).split()))

# Train.
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(cleaned_df)
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = MultinomialNB().fit(X_train_tfidf, df['label'])

# Save for later use.
joblib.dump(count_vect, 'count_vect.pkl')
joblib.dump(tfidf_transformer, 'tfidf_transformer.pkl')
joblib.dump(clf, 'clf.pkl')
