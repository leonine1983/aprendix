import autocomplete_light_registry
from gestao_escolar.models import Alunos

class AlunosAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['nome_completo']  # Campos para pesquisar

autocomplete_light_registry (Alunos, AlunosAutocomplete)