from django.contrib import admin
from .models import *

class TurmasAdmin(admin.ModelAdmin):
    list_display = ('nome', 'escola', 'ano_letivo', 'turma_concluida')
#admin.site.register(AnoLetivo)
admin.site.register(Cargo)
admin.site.register(Profissionais)
admin.site.register(Etnia)
admin.site.register(Alunos)
admin.site.register(Compatibilidade_EducaCenso)
admin.site.register(GrauEscolar)
admin.site.register(Serie_Escolar)
admin.site.register(Turmas, TurmasAdmin)
admin.site.register(Disciplina)
admin.site.register(TurmaDisciplina)
admin.site.register(Remanejamento)
admin.site.register(Matriculas)
# admin.site.register(GestaoTurmas)
admin.site.register(Validade_horario)
admin.site.register(Periodo)
admin.site.register(Horario)
admin.site.register(DiaSemana)
admin.site.register(Presenca)
# Matricula Online
admin.site.register(EscolaMatriculaOnline)
admin.site.register(SerieOnline)
admin.site.register(MatriculasOnline)

#admin.site.register(PerguntasAbertas)
#admin.site.register(PerguntasMultiplaEscolha)
#admin.site.register(OpcaoMultiplaEscolha)
#admin.site.register(PerguntaObjetiva)
#admin.site.register(Notas)
admin.site.register(Trimestre)
admin.site.register(ParecerDescritivo)
admin.site.register(AlunoUser)




class GestaoTurmasAdmin(admin.ModelAdmin):
    list_display = (
        'get_nome_aluno',
        'get_ano_letivo',
        'get_turma',
        'get_disciplina',
        'get_professor',
        'notas',
        'faltas',
        'media_final',
    )
    list_filter = ('trimestre__ano_letivo', 'grade__turma__nome')
    search_fields = ('aluno__aluno__nome_completo', 'grade__disciplina__nome')
    ordering = ('trimestre__ano_letivo__ano', 'aluno__aluno__nome_completo')

    # ✅ Colunas personalizadas:
    def get_nome_aluno(self, obj):
        return obj.aluno.aluno.nome_completo
    get_nome_aluno.short_description = 'Aluno'

    def get_turma(self, obj):
        return obj.grade.turma.nome if obj.grade and obj.grade.turma else '-'
    get_turma.short_description = 'Turma'

    def get_disciplina(self, obj):
        return obj.grade.disciplina.nome if obj.grade and obj.grade.disciplina else '-'
    get_disciplina.short_description = 'Disciplina'

    def get_professor(self, obj):
        if obj.grade and obj.grade.professor:
            return obj.grade.professor.encaminhamento
        return '-'
    get_professor.short_description = 'Professor'

    def get_ano_letivo(self, obj):
        return obj.trimestre.ano_letivo.ano if obj.trimestre and obj.trimestre.ano_letivo else '-'
    get_ano_letivo.short_description = 'Ano Letivo'

admin.site.register(GestaoTurmas, GestaoTurmasAdmin)

