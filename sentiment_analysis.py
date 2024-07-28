import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
from langdetect import detect, LangDetectException

class SentimentAnalysis:
    def __init__(self, keywords):
        self.keywords = keywords
        self.analyzer = SentimentIntensityAnalyzer()

    def fetch_news(self):
        url = f"https://news.google.com/search?q={'+'.join(self.keywords)}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract headlines
            headlines = []
            for title in soup.find_all('a', class_='JtKRv'):
                headline_text = title.get_text(strip=True)
                if self.validate_headline(headline_text):
                    headlines.append(headline_text)
            
            if not headlines:
                for title in soup.find_all('h3', class_='ipQwMb ekueJc RD0gLb'):
                    headline_text = title.get_text(strip=True)
                    if self.validate_headline(headline_text):
                        headlines.append(headline_text)
            
            if not headlines:
                for title in soup.find_all('h3', class_='xrnccd F6Welf R7GTQ keNKEd j7vNaf'):
                    headline_text = title.get_text(strip=True)
                    if self.validate_headline(headline_text):
                        headlines.append(headline_text)
            
            if not headlines:
                print("No valid headlines found.")
                print("Response Content:", response.content)
            
            return headlines
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return []

    def analyze_sentiment(self, headlines):
        if not headlines:
            print("No headlines to analyze.")
            return np.nan, np.nan, np.nan, np.nan, "No Data"
        
        try:
            compound_scores = []
            positive_scores = []
            negative_scores = []
            neutral_scores = []
            
            for headline in headlines:
                sentiment = self.analyzer.polarity_scores(headline)
                compound_scores.append(sentiment['compound'])
                positive_scores.append(sentiment['pos'])
                negative_scores.append(sentiment['neg'])
                neutral_scores.append(sentiment['neu'])

            avg_compound = np.mean(compound_scores)
            avg_positive = np.mean(positive_scores)
            avg_negative = np.mean(negative_scores)
            avg_neutral = np.mean(neutral_scores)
           
            return avg_compound, avg_positive, avg_negative, avg_neutral
        
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return np.nan, np.nan, np.nan, np.nan, "Error"
    
    def validate_headline(self, headline_text):
        # Ensure the headline is not empty and has an appropriate length
        if not headline_text.strip() or len(headline_text) < 15 or len(headline_text) > 150:
            return False
        
        # Check for the presence of common words (basic heuristic)
        common_words = {"the", "is", "in", "and", "to", "of"}
        if not any(word in headline_text.lower() for word in common_words):
            return False
        
        # Exclude headlines with excessive special characters or numbers
        special_chars_count = sum(1 for char in headline_text if not char.isalnum() and not char.isspace())
        if special_chars_count > 5:  # Adjust threshold as necessary
            return False
        
        # Language detection to ensure it's in English (or desired language)
        try:
            language = detect(headline_text)
            if language != 'en':  # Adjust based on desired language
                return False
        except LangDetectException:
            return False
        
        return True

    def process_sentiment_analysis(self):
        # Fetch news headlines
        headlines = self.fetch_news()

        # Analyze sentiment if headlines are valid
        if headlines:
            avg_compound, avg_positive, avg_negative, avg_neutral = self.analyze_sentiment(headlines)
            if not np.isnan(avg_compound):
                print(f"Average compound sentiment score: {avg_compound:.2f}")
                print(f"Average positive sentiment score: {avg_positive:.2f}")
                print(f"Average negative sentiment score: {avg_negative:.2f}")
                print(f"Average neutral sentiment score: {avg_neutral:.2f}")
            else:
                print("Error: Sentiment analysis failed.")
        else:
            print("No valid headlines to analyze.")