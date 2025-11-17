from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

    @classmethod
    def from_string(cls, value: str):
        for sentiment in cls:
            if sentiment.value == value:
                return sentiment
        raise ValueError(f"Invalid sentiment value: {value}")
