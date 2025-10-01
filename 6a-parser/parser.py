import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S P S | S Adv VP | VP Adv
NP -> N | Det NP | Adj NP | NP P NP | NP Adv | NP Conj NP
VP -> V | V NP | VP NP | VP Adv | VP P NP | VP Conj VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Convert sentence to lowercase
    lowercase_sentence = sentence.lower()
    # Tokenize the sentence into words
    tokens = nltk.word_tokenize(lowercase_sentence)
    # Filter out words that do not contain at least one alphabetic character
    words = [word for word in tokens if any(char.isalpha() for char in word)]
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    noun_phrases = []

    # Iterate through all subtrees of the given tree
    for subtree in tree.subtrees():
        # Check if the subtree label is "NP"
        if subtree.label() == "NP":
            # Check if the subtree does not itself contain any other "NP" as subtrees
            if not any(
                child.label() == "NP"
                for child in subtree.subtrees(
                    lambda t: t != subtree
                )  # `subtree.subtrees()` returns all subtrees, including the `subtree` itself. Here, exclude the subtree itself.
            ):
                noun_phrases.append(subtree)

    return noun_phrases


if __name__ == "__main__":
    main()
