#!/usr/bin/env python

# usage: cat train.txt | awk '{print $1}' | ./corrige.py voc-1bwc.txt > output.txt

import sys
from CandidateGenerator import CandidateGenerator

if __name__ == "__main__":

    with open(sys.argv[1]) as lexique_handle:
        words = lexique_handle.readlines()
        words = [word.strip().split() for word in words]
        lexique = {pair[1]: int(pair[0]) for pair in words}

    gen = CandidateGenerator(lexique)

    for line in sys.stdin:
        word = line.rstrip()
        corrected_candidates = gen.correct(word)

        if not corrected_candidates:
            print(word + '\t' + word)
        else:
            corrected_candidates = [candidate[0] for candidate in corrected_candidates]
            final_words = corrected_candidates[:5]
            joined_string = "\t".join(final_words)
            print(word + '\t' + joined_string)
