# schemas/__init__.py

# 1. Importa las clases de tus módulos
from .asistente_schema import AsistenteDBOut
from .materia_schema import MateriaOut

# 2. Llama a model_rebuild() para resolver los strings
#    Esto le dice a Pydantic que busque las clases 'MateriaOut' y 'AsistenteDBOut'
#    y las reemplace en las anotaciones de tipo.
AsistenteDBOut.model_rebuild()
MateriaOut.model_rebuild()