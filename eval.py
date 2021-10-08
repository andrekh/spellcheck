#!/usr/bin/env python
# Lis une liste de mots et leurs corrections sur l'entree standard et calcule un score base sur un dictionnaire fourni comme parametre
# Ex: cat mots-corrige.txt | ./eval.py train.txt
# Le score est affiche sur la sortie standard.

import sys

if __name__ == "__main__":

    total_score = 0
    nwords = 0

    with open(sys.argv[1]) as reference_handle:
        words = reference_handle.readlines()
        words = [word.rstrip().split() for word in words]
        wordic = {wordpair[0]: wordpair[1] for wordpair in words}

    for line in sys.stdin:
        words = (line.strip()).split('\t')
        word_to_correct = words[0]
        suggestions = words[1:]

        score = 0

        if word_to_correct not in wordic:
            continue
        else:
            nwords += 1
        for idx, suggestion in enumerate(suggestions):
            if wordic[word_to_correct] == suggestion:
                score = 1. / (1. + idx)
                break
        total_score += score

    print(total_score / nwords)
