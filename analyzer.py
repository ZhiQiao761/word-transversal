import requests, sys, random, argparse
from anytree import Node, RenderTree
from anytree.exporter import DotExporter

BASE_FORMAT_URL = "https://api.datamuse.com/words?rel_trg={}&topics={}"

def random_iteration(initial, topics, iterations):
    seen_words = [initial]
    start_url = BASE_FORMAT_URL.format(initial, topics)
    response = requests.get(start_url)
    resp_json = response.json()
    curr_ind = random.randint(0, 3)
    potential = resp_json[curr_ind]['word']
    while potential in seen_words:
        curr_ind += 1
        potential = resp_json[curr_ind]['word']
    else:
        seen_words.append(potential)
    for _ in range(0, iterations):
        curr_url = BASE_FORMAT_URL.format(potential, topics)
        response = requests.get(curr_url)
        resp_json = response.json()
        curr_ind = random.randint(0, 3)
        potential = resp_json[curr_ind]['word']
        while potential in seen_words:
            curr_ind += 1
            potential = resp_json[curr_ind]['word']
        else:
            seen_words.append(potential)
    print(seen_words)

def layered_iteration(initial, topics, root, level, max_depth, seen_words, level_words, word_dict):
    if level == max_depth:
        return None
    url = BASE_FORMAT_URL.format(initial, topics)
    response = requests.get(url)
    synonyms = response.json()
    added = 0 
    curr_ind = 0 
    new_words = []
    while added < level_words:
        if curr_ind >= len(synonyms):
                break
        word = synonyms[curr_ind]['word']
        while word in seen_words:
            curr_ind += 1
            if curr_ind >= len(synonyms):
                break
            word = synonyms[curr_ind]['word']
        word_dict[word] = Node(word, parent=root)
        seen_words.append(word)
        if word.endswith('y'):
            seen_words.append(word[:-1] + "ies")
        if word.endswith('ies'):
            seen_words.append(word[:-3] + "y")
        if word.endswith('s'):
            seen_words.append(word[:-1])
        if word.endswith('es'):
            seen_words.append(word[:-2])
        seen_words.append(word + "s")
        seen_words.append(word + "es")
        new_words.append(word)
        added += 1
    for word in new_words:
        layered_iteration(word, topics, word_dict[word], level + 1, max_depth, seen_words,
                          level_words, word_dict)
    
if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument('--initial', '-s', default="hack", help="Initial word to start with")
    main_parser.add_argument('--topics', '-t', nargs=1, default="technology",
                             help="Comma separated topic list to make " \
                                  "sure the words are roughly related to. " \
                                  "Type 'None' for no topics")
    main_parser.add_argument('--iterations', '-i', required=True, type=int,
                             help="Number of iterations/depth to go down")
    main_parser.add_argument('--breadth', '-b', required=False, default=1,
                             help="Number of related words on each depth level")
    args = main_parser.parse_args()
    root = Node(args.initial)
    if args.topics == 'None':
        BASE_FORMAT_URL = "https://api.datamuse.com/words?rel_trg={}"
    seen_words = [args.initial]
    if args.initial.endswith('y'):
        seen_words.append(args.initial[:-1] + "ies")
    if args.initial.endswith('ies'):
        seen_words.append(args.initial[:-3] + "y")
    if args.initial.endswith('s'):
        seen_words.append(args.initial[:-1])
    if args.initial.endswith('es'):
        seen_words.append(args.initial[:-2])
    seen_words.append(args.initial + "s")
    seen_words.append(args.initial + "es")
    layered_iteration(args.initial, args.topics, root, 0, args.iterations, 
                      seen_words, int(args.breadth), {})
    print(RenderTree(root))
    DotExporter(root).to_picture("./root.png")