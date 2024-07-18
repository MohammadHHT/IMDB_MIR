import re
import json
import string
from collections import defaultdict

import nltk
from nltk.tokenize import word_tokenize
try:
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
except:
    nltk.download('stopwords')
    nltk.download('wordnet')
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer


class Preprocessor:

    def __init__(self, documents: list):
        """
        Initialize the class.

        Parameters
        ----------
        documents : list
            The list of documents to be preprocessed, path to stop words, or other parameters.
        """
        # TODO
        self.documents = documents
        self.stopwords = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

            

    def preprocess(self):
        """
        Preprocess the text using the methods in the class.

        Returns
        ----------
        List[str]
            The preprocessed documents.
        """
        # TODO
        preped = list()
        for doc in self.documents:
            temp_doc = defaultdict(list)
            for key in doc.keys():
                if isinstance(doc[key], list):
                    if key == 'reviews':
                        for text, score in doc[key]:
                            text = self.remove_links(text)
                            text = self.remove_punctuations(text)
                            text = self.normalize(text)
                            temp_doc[key].append((text, score))
                    else:
                        for text in doc[key]:
                            text = self.remove_links(text)
                            text = self.remove_punctuations(text)
                            text = self.normalize(text)
                            temp_doc[key].append(text)
                    
                else:
                    text = self.remove_links(str(doc[key]))
                    text = self.remove_punctuations(text)
                    text = self.normalize(text)
                    temp_doc[key] = text
            preped.append(temp_doc)
        return preped

    def normalize(self, text: str):
        """
        Normalize the text by converting it to a lower case, stemming, lemmatization, etc.

        Parameters
        ----------
        text : str
            The text to be normalized.

        Returns
        ----------
        str
            The normalized text.
        """
        #* DONE
        text = text.lower()
        words = self.tokenize(text)
        leman_words = [self.lemmatizer.lemmatize(word) for word in words]
        return ' '.join(leman_words)

    def remove_links(self, text: str):
        """
        Remove links from the text.

        Parameters
        ----------
        text : str
            The text to be processed.

        Returns
        ----------
        str
            The text with links removed.
        """
        patterns = [r'\S*http\S*', r'\S*www\S*', r'\S+\.ir\S*', r'\S+\.com\S*', r'\S+\.org\S*', r'\S*@\S*']
        #* DONE
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        return text

    def remove_punctuations(self, text: str):
        """
        Remove punctuations from the text.

        Parameters
        ----------
        text : str
            The text to be processed.

        Returns
        ----------
        str
            The text with punctuations removed.
        """
        #* DONE
        return text.translate(str.maketrans('', '', string.punctuation))

    def tokenize(self, text: str):
        """
        Tokenize the words in the text.

        Parameters
        ----------
        text : str
            The text to be tokenized.

        Returns
        ----------
        list
            The list of words.
        """
        #* DONE
        return [word for word in word_tokenize(text) if word not in self.stopwords]

    def remove_stopwords(self, text: str):
        """
        Remove stopwords from the text.

        Parameters
        ----------
        text : str
            The text to remove stopwords from.

        Returns
        ----------
        list
            The list of words with stopwords removed.
        """
        # TODO
        #! Nope
        return
