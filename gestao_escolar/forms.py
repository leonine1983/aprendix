# forms.py
from django import forms
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Submit
from .models import Question, MultipleChoiceAnswer, OpenEndedAnswer

class MultipleChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

    question = forms.ModelChoiceField(queryset=Question.objects.all(), empty_label=None)
    answer = forms.ModelChoiceField(queryset=MultipleChoiceAnswer.objects.none())

    def clean(self):
        cleaned_data = super().clean()
        question = cleaned_data.get('question')
        answer = cleaned_data.get('answer')

        if question and answer:
            if not answer.is_correct:
                self.add_error('answer', 'Resposta incorreta.')

class OpenEndedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

    question = forms.ModelChoiceField(queryset=Question.objects.all(), empty_label=None)
    answer = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        question = cleaned_data.get('question')
        answer = cleaned_data.get('answer')

        if question and answer:
            # Aqui você pode aplicar validações adicionais à resposta aberta
            pass
