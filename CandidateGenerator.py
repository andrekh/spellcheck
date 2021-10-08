from editor import editor
from utils import softmax
from metaphone import doublemetaphone
import numpy as np
from DictionaryProcessor import DictionaryProcessor
import jellyfish


class CandidateGenerator:
    def __init__(self, lexique, parameters):
        self.lexique = lexique
        self.ntot = sum(self.lexique.values())
        self.parameters = parameters
        self.dp = DictionaryProcessor(lexique)

    def correct(self, word):

        edited_words = editor(word)
        candidates_from_edit = edited_words.intersection(self.lexique.keys())

        # get suggestions from the hashing method but penalize them
        candidates_from_hash = self.dp.ReturnMatchedTokens(word)
        candidates_list = sorted(candidates_from_edit.union(candidates_from_hash))

        if not candidates_list:
            return None

        penalty_logits = []
        for candidate in candidates_list:
            if candidate in candidates_from_hash and candidate not in candidates_from_edit:
                penalty_logits.append(-0.2)
            else:
                penalty_logits.append(0)
        penalty_logits = np.array(penalty_logits)

        # compute p(c) for each candidate
        size_of_vocab = len(self.lexique)
        pc = np.array([(self.lexique[candidate] + 1) / (self.ntot + size_of_vocab) for candidate in candidates_list])
        pc_logits = np.log(pc / (1.001 - pc))

        # compute p(wc)
        # 1. prob based on edit distance
        edit_distances = np.array([jellyfish.jaro_similarity(word, candidate) for candidate in candidates_list])
        prob_edit_distances = softmax(edit_distances)
        prob_edit_distances_logits = np.log(prob_edit_distances / (1.001 - prob_edit_distances))

        # 2. prob based on metaphone
        metaphone_word = doublemetaphone(word)[0] + doublemetaphone(word)[1]
        metaphone_distances = np.array(
            [jellyfish.jaro_similarity(metaphone_word, doublemetaphone(candidate)[0] + doublemetaphone(candidate)[1])
             for candidate in candidates_list])
        prob_metaphone_distances = softmax(metaphone_distances)
        prob_metaphone_distances_logits = np.log(prob_metaphone_distances / (1.001 - prob_metaphone_distances))

        # 3. combine the logits and take the softmax
        # the coefficients have been tuned experimentally
        combined_logits = 0.04278 * pc_logits + 0.7035 * prob_edit_distances_logits + \
                          0.25374 * prob_metaphone_distances_logits + penalty_logits
        combined_prob = softmax(combined_logits).tolist()
        candidates_list = [[candidate, prob] for candidate, prob in zip(candidates_list, combined_prob)]
        candidates_list.sort(key=lambda x: x[1], reverse=True)

        return candidates_list
