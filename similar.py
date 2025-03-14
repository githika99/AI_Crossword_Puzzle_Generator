import random
import wikipediaapi
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import string

def wikipediaData(theme, max_sentences=2):
    user_agent = "proj/1.0 (abc@def.com)"
    wiki = wikipediaapi.Wikipedia(language="en", user_agent=user_agent)
    theme = " ".join(word.capitalize() for word in theme.split(" "))
    page = wiki.page(theme)

    if page.exists():
        # handling disambiguation pages (pages where a term may mean multiple things)
        if "may refer to" in page.summary.lower():
            disambLinks = list(page.links.keys())
            if disambLinks:
                chosen = random.choice(disambLinks)
                page = wiki.page(chosen)
                if not page.exists():
                    return None
                
        full_content = page.text

        # Optionally truncate to `max_sentences`
        sentences = full_content.split(". ")
        truncated_content = ". ".join(sentences[:max_sentences])
        return truncated_content
    else:
        return None

def extractWords(summary):
    if not summary:
        return []

    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(summary.lower())
    keywords = {
        word for word in tokens 
        if word.isalnum() and word not in stop_words and word not in string.punctuation
    }
    unwanted = """aboard about above across
                after against along among
                around as at before
                behind below beneath beside
                between beyond but by
                despite down during except
                failing following for from
                in inside into like
                minus near next of
                off on onto opposite
                out outside over past
                plus regarding since than
                through throughout till to
                toward towards under underneath
                unlike until up upon
                via with within without
                whose unlike either
                contain various use
                near often also another apart
                someone, together, many ga area
                part known consist sections
                occurs last consists built
                group other others dg studios"""
    obscenities = """piss pee"""
    # filter out common words used in wikipedia
    keywords = [x for x in keywords if x not in re.split("\n| ", unwanted)]
    # filter out obscenities
    keywords = [x for x in keywords if x not in re.split("\n| ", obscenities)]
    # filter out two-letter words
    keywords = [x for x in keywords if len(x) > 2]
    # filter out all words that might not be related to the theme
    keywords = [x for x in keywords if not x.endswith(("ing", "ed", "es", "ly"))]

    return keywords

def getWords(theme, maxWords, pos=None):
    titleWords = "the of and to with"
    theme = theme.split(' ')
    theme = ' '.join([x for x in theme if x not in re.split("\n ", titleWords)])
    relatedWords = set()

    pgSummary = wikipediaData(theme)
    if pgSummary:
        wikiKeywords = extractWords(pgSummary)
        relatedWords.update(wikiKeywords)
        for word in wikiKeywords:
            relatedWords.add(word)
        # choose first n words in wikipedia extraction + theme to be used as themes for more data
        wikiKeywords = [x for x in wikiKeywords if x.islower() and x.isalpha() and x.isascii()]
        print(f"words chosen for extraction: {wikiKeywords[:3]}")
        for term in wikiKeywords[:3]:
            termSynsets = wordnet.synsets(term, pos=pos)
            for synset in termSynsets:
                for meronym in synset.part_meronyms():
                    for lemma in meronym.lemmas():
                        relatedWords.add(lemma.name())
                for hypernym in synset.hypernyms():
                    for lemma in hypernym.lemmas():
                        relatedWords.add(lemma.name())

    themeSynsets = wordnet.synsets(theme, pos=pos)
    for synset in themeSynsets:
        for lemma in synset.lemmas():
            relatedWords.add(lemma.name())
        for meronym in synset.part_meronyms():
            for lemma in meronym.lemmas():
                relatedWords.add(lemma.name())
        for hypernym in synset.hypernyms():
            for lemma in hypernym.lemmas():
                relatedWords.add(lemma.name())

    # remove numbers, hyphenated words, and phrases
    relatedWords = {x for x in relatedWords if x.islower() and x.isalpha() and x.isascii()}
    # remove the target word if it appears in there (it happens!)
    relatedWords = {x for x in relatedWords if x != theme}
    remove_plural_words(relatedWords)

    return list(relatedWords)[:maxWords]

def remove_plural_words(wordList):
    singularWords = set(wordList)  # Convert the list to a set for faster lookup
    filter = [
        word for word in wordList 
        if not (word.endswith("s") and word[:-1] in singularWords)
    ]
    return filter
