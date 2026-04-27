import spacy
from spacy.matcher import PhraseMatcher
from .neo4jKG import neo4jKG
class TripleExtractorSpacy:
    def __init__(self, neo4j):
        self.nlp = spacy.load("zh_core_web_trf")
        self.kg = neo4j
        self.terms = self.kg.get_entities_names()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        patterns = [self.nlp.make_doc(term) for term in self.terms]
        self.matcher.add("TechTerms", patterns)

    def extract_triples(self, text):
        """
        提取主谓宾三元组，并通过字符索引修复属于错误
        """
        doc = self.nlp(text)
        triples = []

        for token in doc:
            if token.pos_ == "VERB":
                subject = None
                obj = None
                prep_obj = None

                for child in token.children:
                    if child.dep_ == "nsubj":
                        subject = self._match_full_term(child.idx, text)
                    elif child.dep_ == "dobj":
                        obj = self._match_full_term(child.idx, text)
                    elif child.dep_ == "prep":
                        for grandchild in child.children:
                            if grandchild.dep_ == "pobj":
                                prep_obj = self._match_full_term(grandchild.idx, text)
                if subject and (obj or prep_obj):
                    triples.append((subject, token.text, obj or prep_obj))
        return triples

    def _match_full_term(self, start_idx, text):
        """给定字符位置，尝试返回完整的属于或原token"""
        # 优先匹配术语
        for term in self.terms:
            if text.find(term, start_idx) == start_idx:
                return term

        # 否则返回原始token文本
        for token in self.nlp(text):
            if token.idx <= start_idx < token.idx +len(text):
                return token.text
        return text[start_idx:start_idx + 10]

    def named_entity_recognition(self,question):
        """使用PhraseMatcher匹配预定义的技术术语，并返回去重结果"""
        doc = self.nlp(question)
        matches = self.matcher(doc)
        matched_terms = list(set(doc[start:end].text for _, start, end in matches))
        return matched_terms
