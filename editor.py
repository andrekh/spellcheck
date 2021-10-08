def editor(word):
    chars = 'abcdefghijklmnopqrstuvwxyz'
    removed = [word[:n] + word[n + 1:] for n in range(len(word))]
    swapped = [word[:-len(word) + n] + word[n + 1] + word[n] + word[n + 2:] for n in range(len(word) - 1)]
    inserted = [*[s + word for s in chars], *[word + s for s in chars],
                *[word[:n] + char + word[n:] for char in chars for n in range(1, len(word))]]
    replaced = [word[:n] + s + word[n + 1:] for s in chars for n in range(len(word))]
    return set(removed + swapped + inserted + replaced)
