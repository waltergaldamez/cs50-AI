import os
import random
import re
import sys
import math

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
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probs = dict()

    # At a minimum, every page has a combined (1-damping_factor) probability of being selected
    for p in corpus:
        probs[p] = (1 - damping_factor) / len(corpus)
    
    linkedPages = corpus[page + ".html"]

    # if there are no links in the current page, then the damping_factor gets distributed evenly across ALL pages
    if len(linkedPages) == 0:
        for p in corpus:
            probs[p] = probs[p] + damping_factor / len(corpus)
    # Otherwise, the damping factor is distributed evenly (among the pages being linked to) 
    # and added to the minimum probability assigned at the beginning of the function
    else:
        for p in linkedPages:
            probs[p] = probs[p] + damping_factor / len(linkedPages)
    return probs

def get_random_page(probs):
    # generate a random number between 1 - 100
    rand_num = math.floor(random.random() * 100) + 1
    sum = 0
    # iterate through all the probabilites and sum them. 
    # The random page will be the one where the random number falls in the range of the prev sum + the next probability in the distributioin
    for page in probs:
        sum += (probs[page] * 100)
        if rand_num <= sum:
            return page
    return list(probs.keys())[-1]

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probs = dict()
    # initialize return dictionary
    for page in corpus:
        probs[page] = 0
    num_pages = len(corpus)
    # randomly generate the first page
    curr_page = math.floor(random.random() * num_pages) + 1
    num_pages = 1
    for page in corpus:
        if num_pages == curr_page:
            curr_page = page
        num_pages += 1
    probs[curr_page] = 1

    # run for n -1 remaining samples
    for i in range(1, n):
        next_prob = transition_model(corpus, remove_suffix(curr_page, ".html"), damping_factor)
        curr_page = get_random_page(next_prob)
        probs[curr_page] += 1
    
    # get the distrubtion of the samples by dividing by total number of samples
    for page in probs:
        probs[page] = probs[page] / n
    
    return probs


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    iterate_pr = dict()
    # diff is a flag used to terminate the loop when the difference in no longer greater than 0.001
    diff = True

    # initially, all pages take equal probability
    for page in corpus:
        iterate_pr[page] = 1 / len(corpus)
    
    while diff is True:
        diff = False
        prev_pr = iterate_pr.copy()
        for page in iterate_pr:
            # left hand side of the iteration formula
            new_pr = ((1 - damping_factor) / len(corpus))
            parents = [link for link in corpus if page in corpus[link]]
            summation = 0

            # summation part of the iteration formula
            for parent in parents:
                summation = summation + (prev_pr[parent] / len(corpus[parent]))
            #right hand side of the iteration formula
            new_pr = new_pr + (damping_factor * summation)
            if abs(new_pr - prev_pr[page]) > 0.001:
                diff = True
            iterate_pr[page] = new_pr
    dictsum = (sum(iterate_pr.values()))
    iterate_pr = {key: value/dictsum for key, value in iterate_pr.items()}
    return iterate_pr


if __name__ == "__main__":
    main()
