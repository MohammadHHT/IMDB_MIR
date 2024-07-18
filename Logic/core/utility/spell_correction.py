from collections import Counter, defaultdict


class SpellCorrection:
    def __init__(self, all_documents):
        """
        Initialize the SpellCorrection

        Parameters
        ----------
        all_documents : list of str
            The input documents.
        """
        self.all_shingled_words, self.word_counter = self.shingling_and_counting(all_documents)

    def shingle_word(self, word, k=2):
        """
        Convert a word into a set of shingles.

        Parameters
        ----------
        word : str
            The input word.
        k : int
            The size of each shingle.

        Returns
        -------
        set
            A set of shingles.
        """
        
        #* DONE: Create shingle here
        shingles = {word[i:i+k] for i in range(len(word) - k + 1)}

        return shingles
    
    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score.

        Parameters
        ----------
        first_set : set
            First set of shingles.
        second_set : set
            Second set of shingles.

        Returns
        -------
        float
            Jaccard score.
        """

        #* DONE: Calculate jaccard score here.
        intersection = len(first_set.intersection(second_set))
        union = len(first_set.union(second_set))

        return intersection / union if union else 0.0

    def shingling_and_counting(self, all_documents):
        """
        Shingle all words of the corpus and count TF of each word.

        Parameters
        ----------
        all_documents : list of str
            The input documents.

        Returns
        -------
        all_shingled_words : dict
            A dictionary from words to their shingle sets.
        word_counter : dict
            A dictionary from words to their TFs.
        """

        # TODO: Create shingled words dictionary and word counter dictionary here.
        all_shingled_words = defaultdict(set)
        word_counter = Counter()

        for document in all_documents:
            words = document.split()
            word_counter += Counter(words)
            for word in words:
                all_shingled_words[word].union(self.shingle_word(word))

        return all_shingled_words, word_counter
    
    def find_nearest_words(self, word):
        """
        Find correct form of a misspelled word.

        Parameters
        ----------
        word : stf
            The misspelled word.

        Returns
        -------
        list of str
            5 nearest words.
        """

        # TODO: Find 5 nearest candidates here.
        shingled_word = self.shingle_word(word)
        candidates = []

        for candidate_word, candidate_shingles in self.all_shingled_words.items():
            if score := self.jaccard_score(shingled_word, candidate_shingles) > 0:
                candidates.append((candidate_word, score))

        candidates.sort(key=lambda x: x[1])
        top5_candidates = [t[0] for t in candidates[:-6:-1]]

        return top5_candidates
    
    def spell_check(self, query):
        """
        Find correct form of a misspelled query.

        Parameters
        ----------
        query : stf
            The misspelled query.

        Returns
        -------
        str
            Correct form of the query.
        """

        # TODO: Do spell correction here.

        final_result = ""
        words = query.split()
        corrected_query = []

        for word in words:
            if nearest_words := self.find_nearest_words(word):
                word = nearest_words[0]
            corrected_query.append(word)
        final_result = " ".join(corrected_query)

        return final_result