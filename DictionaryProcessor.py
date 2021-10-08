from collections import defaultdict
from editor import editor


class DictionaryProcessor:

    def __init__(self, lexique):
        self.lexique = lexique
        self.hashdic = self.BuildHashTable()

    def RemoveVowels(self, word):
        vowels = ('a', 'e', 'i', 'o', 'u', 'y')
        new_word = ''.join([letter for letter in word if letter not in vowels])
        return new_word

    def BuildHashTable(self):
        processed_dic = defaultdict(list)
        for word in self.lexique.keys():
            # add new hashing ideas here
            new_word = self.RemoveVowels(word)
            processed_dic[new_word].append(word)
        return processed_dic

    def ReturnMatchedTokens(self, word):

        # vowel removal
        vowels_removed = self.RemoveVowels(word)
        edited_tokens = editor(vowels_removed)

        # f->ph
        fph = vowels_removed.replace('f', 'ph')
        edited_tokens = edited_tokens.union(editor(fph))
        edited_tokens.add(fph)

        tokens_set = set(self.hashdic[vowels_removed] + self.hashdic[fph])

        for token in edited_tokens:
            tokens_set = tokens_set.union(self.hashdic[token])
        # returns a set of oandidate correct words
        return tokens_set
