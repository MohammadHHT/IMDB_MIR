import nltk
from nltk.tokenize import word_tokenize
try:
    from nltk.corpus import stopwords
except:
    nltk.download('stopwords')
    from nltk.corpus import stopwords


class Snippet:
    def __init__(self, number_of_words_on_each_side=5):
        """
        Initialize the Snippet

        Parameters
        ----------
        number_of_words_on_each_side : int
            The number of words on each side of the query word in the doc to be presented in the snippet.
        """
        self.number_of_words_on_each_side = number_of_words_on_each_side
        self.stopwords = set(stopwords.words('english'))

    def remove_stop_words_from_query(self, query):
        """
        Remove stop words from the input string.

        Parameters
        ----------
        query : str
            The query that you need to delete stop words from.

        Returns
        -------
        str
            The query without stop words.
        """

        #* DONE: remove stop words from the query.

        words = query.lower().split()
        filtered_words = [word for word in words if word not in self.stop_words]
        return ' '.join(filtered_words)

    def find_snippet(self, doc, query):
        """
        Find snippet in a doc based on a query.

        Parameters
        ----------
        doc : str
            The retrieved doc which the snippet should be extracted from that.
        query : str
            The query which the snippet should be extracted based on that.

        Returns
        -------
        final_snippet : str
            The final extracted snippet. IMPORTANT: The keyword should be wrapped by *** on both sides.
            For example: Sahwshank ***redemption*** is one of ... (for query: redemption)
        not_exist_words : list
            Words in the query which don't exist in the doc.
        """
        final_snippet = ""
        not_exist_words = []

        # TODO: Extract snippet and the tokens which are not present in the doc.

        filtered_query = self.remove_stop_words_from_query(query)
        doc_words = doc.split()

        snippets = []
        not_exist_words = []

        for word in filtered_query.split():
            if word in doc_words:
                word_idx = doc_words.index(word)
                start = max(word_idx - self.number_of_words_on_each_side, 0)
                end = min(word_idx + self.number_of_words_on_each_side + 1, len(doc_words))
                snippet = doc_words[start:word_idx] + [f'***{word}***'] + doc_words[word_idx + 1:end]
                snippets.append(' '.join(snippet))
            else:
                not_exist_words.append(word)

        final_snippet = ' ... '.join(snippets)

        return final_snippet, not_exist_words