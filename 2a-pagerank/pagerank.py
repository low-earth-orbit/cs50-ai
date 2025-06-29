import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    N = len(corpus)
    distribution = dict()
    links = corpus[page]
    if links:  # if there is a link on the page
        for page in corpus:
            distribution[page] = (1 - damping_factor) / N
            if page in links:
                distribution[page] += damping_factor / len(links)
    else:  # if there is no links on the page
        for page in corpus:
            distribution[page] = 1 / N
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    visit_counts = {page: 0 for page in corpus}
    first_page = random.choice(list(corpus.keys()))
    visit_counts[first_page] += 1
    current_page = first_page
    for i in range(2, n + 1):  # from 2 to n
        page_distribution = transition_model(corpus, current_page, damping_factor)
        next_page = random.choices(
            population=list(page_distribution.keys()),
            weights=list(page_distribution.values()),
            k=1,
        )[0]
        visit_counts[next_page] += 1
        current_page = next_page
    pagerank = {page: count / n for page, count in visit_counts.items()}
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pageranks = {page: 1 / N for page in corpus}
    THRESHOLD = 0.001
    while True:
        new_pageranks = {}

        for page in corpus:  # for each page in corpus
            sum = 0
            for i in corpus:  # check every other page
                if corpus[i]:  # if the other page has links
                    if (
                        page in corpus[i]
                    ):  # if this page is linked in the links of other page
                        sum += pageranks[i] / len(corpus[i])
                else:  # if the other page has no links
                    sum += pageranks[i] / N
            new_pageranks[page] = (1 - damping_factor) / N + damping_factor * sum

        # check stop criterion
        stop = all(
            abs(new_pageranks[page] - pageranks[page]) < THRESHOLD for page in pageranks
        )
        pageranks = new_pageranks
        if stop:
            break

    return pageranks


if __name__ == "__main__":
    main()
