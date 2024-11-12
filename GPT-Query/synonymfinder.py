import dictionary_parser
import json
import os
import re
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import nltk

# Ensure necessary NLTK data packages are downloaded
nltk.download('wordnet')
nltk.download('omw-1.4')  # WordNet's extended data
nltk.download('stopwords')


