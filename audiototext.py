import speech_recognition as sr
from rake_nltk import Rake
from textblob import TextBlob
from textblob.en import sentiment
from gensim import corpora
from gensim.models import LdaModel



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
            return "audio cloud not be understood"

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
    elif sentiment > 0.5:
        return "Positive"
    else:
        return "Neutral"

def topic_modeling(text):
    words = text.split() # ["hello", "this", "is", "scott"]
    dictionary = corpora.Dictionary([words]) # {0: "hello", 1: "this", ....}
    corpus = [dictionary.doc2bow(words)] # {"hello": 1, .."}
    lda_model = LdaModel(corpus, num_topics = 3, id2word=dictionary)
    topics = lda_model.print_topics(num_words = 3)
    return topics

text = audio_to_text(audio)
print(extract_sentiments(text))
print(topic_modeling(text))
print(extract_keywords(text))
