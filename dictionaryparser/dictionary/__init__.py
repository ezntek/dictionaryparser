from ..parser import Definition

class Dictionary:
    def __init__(self, definitions: list[Definition]) -> None:
        # linear searches are slow, store the word as the key and the whole definition as the value
        self.definitions = definitions


    def search_word(self, search_term: str) -> list[Definition]:
        res = list()
        predicate = lambda word: (search_term in word or search_term == word)

        for definition in self.definitions:
            if predicate(definition.word):
                res.append(definition)
     
        return res

    def search_definition(self, search_term: str) -> list[Definition]:
        res = list()
        predicate = lambda definition: (search_term in definition)

        for definition in self.definitions:
            if predicate(definition.definition):
                res.append(definition)

        return res
                
