# from typing import List, Text

# from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase

# """
# Class that implements the knowledge base for the TMDB movie database.
# It inherits from the InMemoryKnowledgeBase class in order to use the default implementation of the methods.
# """
# class TMDBKnowledgeBase(InMemoryKnowledgeBase):
#     def __init__(self):
#         super().__init__()
    
#     async def get_attributes_of_object(self, object_type: Text) -> List[Text]:
#         """ Get the attributes of the given object type ( TMDB json dictionary )"""
#         if object_type not in self.data or not self.data[object_type]:
#             return []
#         return list(self.data[object_type][0].keys())