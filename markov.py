import random
import cPickle
import shelve

def generateText(corpus, keyFile, seed, numSentences=4):
	keys = cPickle.load(keyFile) #TODO: as a text file
	seed = random.choice(keys).split()
	text = []
	text.extend(seed)
	sentenceCount = 0
	while sentenceCount < 5:
		try:
			word = random.choice(corpus[' '.join(seed)])
			text.append(word)
			seed.append(word)
			seed.pop(0)
			if word.endswith('.'):
				sentenceCount += 1
		except KeyError:
			seed = random.choice(keys).split()
	
	return ' '.join(text)

def generate():
	corpus = shelve.open('markov')
	keyFile = open('markov_keys')
	text = generateText(corpus, keyFile, "those attacks are")
	corpus.close()
	keyFile.close()
	return text

print generate()