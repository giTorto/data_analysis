import sys
import cherrypy as http
import pickle, os
import spacy
import CRFPP

class DialogueActTagger:
    def __init__(self, subj=None,spacy_inst=None):
        self.ynModel=CRFPP.Tagger("-m models/YNmodelViolent -v 3 -n2")
        self.nlp=spacy_inst
    def get_best_DA(self,tagger,size):
        bestP=0
        bestTag=""
        for i in range(0,size):
            if tagger.prob(0,i)>bestP:
                bestTag=tagger.yname(i)
                bestP=tagger.prob(0,i)
        return (bestTag,bestP)
    @http.expose
    def classifyYN(self,sentence):
        self.ynModel.clear()
        l=len(sentence.split(" "))
        doc=self.nlp(sentence.decode("unicode-escape"))
        for w in doc:
            self.ynModel.add(str(w.text)+"\t"+str(w.lemma_)+"\t"+str(w.tag_)+"\t"+str(w.ent_iob)+"\t"+str(w.dep_)+"\t"+str(l))
        self.ynModel.parse()
        tag=self.get_best_DA(self.ynModel,2)
        #print tag,sentence
        return tag[0]
if __name__ == "__main__":
    x=DialogueActTagger(spacy_inst=spacy.load("en"))
    http.config.update({'server.socket_host': "0.0.0.0", 'server.socket_port': 5500})
    http.quickstart(x)
