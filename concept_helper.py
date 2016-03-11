#!/usr/bin/python
import math
from textblob import TextBlob as tb

def tf(word, blob):
  return float(blob.words.count(word)) / len(blob.words)

def n_containing(word, bloblist):
  return sum(1 for blob in bloblist if word in blob)

def idf(word, bloblist):
  #print "word:",word,"bloblist length",len(bloblist),"ncontain",n_containing(word,bloblist)
  return math.log(len(bloblist) / float((1 + n_containing(word, bloblist))))

def tfidf(word, blob, bloblist):
  t = tf(word, blob)
  i = idf(word, bloblist)
  return t * i


class concept_helper:
  """ Code borrowed from http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/"""
  bloblist = None
  def __init__(self,graph):
    self.bloblist = []
    for node in graph.nodes():
      try:
        self.bloblist.append(tb(graph.node[node]['abstract']))
      except:
        print "No abstract for node ",node

  def extract(self,graph,abs1,abs2, num_concepts):
    textblob = ''
    textblob += abs1.lower()
    textblob += abs2.lower()
    textblob = tb(textblob)
    scores = {word: tfidf(word,textblob,self.bloblist) for word in textblob.words}
    sorted_words = sorted(scores.items(), key=lambda x: x[1])
    for word,score in sorted_words[:-1 * num_concepts]:
      print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
    a = [x[0] for x in sorted_words[:-1*num_concepts]]
    return a[-num_concepts:]
