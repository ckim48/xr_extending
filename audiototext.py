import speech_recognition as sr
from rake_nltk import Rake
from textblob import TextBlob
from gensim import corpora
from gensim.models import LdaModel
from collections import Counter

# Hello, World ->
# hello, world
# ["hello," ,"world"]
stop_words = {"a","the","is","are","am","i"}
def count_word_frequency(input_string):
    words = input_string.lower().split()
    words = [word.strip(".,!?;:") for word in words]
    filtered_words = [word for word in words if word not in stop_words]
    # ["hi", "sad", "my", name", ....]
    word_count = Counter(filtered_words)
    return  word_count

sample ="I worry about my relationship with my friends"
print(count_word_frequency(sample))

audio = "sample.wav"
def audio_to_text(audio):
    with sr.AudioFile(audio) as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "audio could not be understood"
def extract_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()
    return keywords
def extract_sentiments(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment < -0.5:
        return "Negative"
    elif -0.5 <= sentiment <= 0.5:
        return "Neutral"
    else:
        return "Positive"

def topic_modeling(text): # "hello this is scott"
    words = text.split() # ["hello","this","is","scott"]
    dictionary = corpora.Dictionary([words]) # {0:"hello", 1:"this",..."}
    corpus = [dictionary.doc2bow(words)] # {"hello":1,.."
    lda_model = LdaModel(corpus, num_topics = 3, id2word=dictionary)
    topics = lda_model.print_topics(num_words = 3)
    return topics


text = audio_to_text(audio)
print(extract_sentiments(text))
print(topic_modeling(text))
print(extract_keywords(text))

