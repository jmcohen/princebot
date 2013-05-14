import random
import cPickle
import shelve

def buildMarkov(filename, N):
	tuples = {}

	f = open(filename)

	for line in f:
		words = line.split()
		sequence = []
		for word in words:
			if len(sequence) == N:
				seq = tuple(sequence)
				if seq in tuples:
					tuples[seq].append(word)
				else:
					tuples[seq] = [word]

				sequence.pop(0)
			sequence.append(word)

	f.close()

	return tuples

def writeMarkov(tuples, dictFilename, keysFilename):
	markov = shelve.open(dictFilename)
	for tupkey in tuples.keys():
		key = ' '.join(tupkey)
		values = tuples[tupkey]
		markov[key] = values
	markov.close()

	f = open(keysFilename, 'w')
	keys = [' '.join(tupkey) for tupkey in tuples.keys() if tupkey[0][0] == tupkey[0][0].title()]
	cPickle.dump(keys, f, cPickle.HIGHEST_PROTOCOL)
	f.close()

print "Building Markov model"
tuples = buildMarkov("comments", 3)
print "Writing Markov model"
writeMarkov(tuples, 'markov', 'markov_keys')

