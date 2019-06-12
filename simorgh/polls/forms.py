from django import forms
from .models import Choice, Question
from django.forms import ModelForm, formset_factory
from django.forms.widgets import RadioSelect

class ChoiceForm(ModelForm):
    EXCELLENT, GOOD, MEDIUM, BAD = 'EX', 'GO', 'ME', 'BA'
    question_choices = (
        (EXCELLENT, 'عالی'),
        (GOOD, 'خوب'),
        (MEDIUM, 'متوسط'),
        (BAD, 'ضعیف')
    )
    choice_text = forms.ChoiceField(choices=question_choices, widget=RadioSelect(attrs={"required":"required"}), required=True)

    class Meta:
        model = Choice
        fields = ['choice_text']


ChoiceFormset = formset_factory(ChoiceForm, extra=Question.objects.count())