import os
import random

import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

project_dir = os.path.abspath(os.path.dirname(__file__) + os.sep + os.pardir)
project_name = os.path.basename(project_dir)


bad_keywords = {
    "sex",
    "violent",
    "war",
    "child",
    "porn",
    "abuse",
    "racist",
    "illegal",
    "anger",
    "depression",
    "sad",
    "bad",
    "negative",
    "pain",
}

ps = PorterStemmer()


def tokenstem(text):
    tokens = word_tokenize(text)
    for token in tokens:
        yield ps.stem(token)


def generate_words():
    words = []
    ignored = []
    dropped = []
    for synset in list(wn.all_synsets()):
        name = synset.lemmas()[0].name().lower()
        definition = synset.definition().lower()
        if len(name) > 5 or not name.isalpha():
            ignored.append(name)
            continue

        stems = set(tokenstem(definition))
        if len(stems.intersection(bad_keywords)) > 0:
            dropped.append(name)
            continue
        words.append(name)

    return list(set(words)), list(set(dropped)), list(set(ignored))


def main():
    nltk.download("wordnet")
    nltk.download("punkt")

    words, dropped, ignored = generate_words()
    random.Random(123).shuffle(words)

    print(f"Retained words count: {len(words)}")
    print(f"Ignored words count: {len(ignored)}")
    print(f"Dropped words count: {len(dropped)}")

    pathname = f"{project_dir}/src/mltraq/utils/wordlist.py"
    with open(pathname, "w") as f:
        f.write(f"words = {words}")

    print(f"Wordlist persisted at {pathname}.")


if __name__ == "__main__":
    main()
