# polls/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import generic
from django.contrib.auth.models import User
from .models import Question, Choice, Vote, UserProfile
from .forms import SignUpForm, ProfileUpdateForm


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Показываем только активные вопросы (в пределах времени жизни).
        """
        now = timezone.now()
        return Question.objects.filter(
            pub_date__lte=now,
            pub_date__gte=now - models.F('lifespan_days') * models.DurationField()
        ).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Проверяем, голосовал ли пользователь
        if self.request.user.is_authenticated:
            context['has_voted'] = Vote.objects.filter(user=self.request.user, question=self.object).exists()
        else:
            context['has_voted'] = False
        return context


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_votes = sum(choice.votes for choice in self.object.choice_set.all())
        results = []
        for choice in self.object.choice_set.all():
            percent = round((choice.votes / total_votes) * 100, 1) if total_votes > 0 else 0
            results.append({'choice': choice, 'percent': percent})
        context['results'] = results
        return context


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.is_active():
        messages.error(request, "Голосование по этому вопросу завершено.")
        return redirect('polls:index')

    if not request.user.is_authenticated:
        return redirect('polls:login')

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Пожалуйста, выберите вариант.',
            'has_voted': False,
        })

    # Проверяем, уже голосовал ли пользователь
    if Vote.objects.filter(user=request.user, question=question).exists():
        messages.warning(request, "Вы уже голосовали в этом опросе.")
        return redirect('polls:results', pk=question.id)

    # Записываем голос
    selected_choice.votes += 1
    selected_choice.save()

    Vote.objects.create(user=request.user, question=question, choice=selected_choice)

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def register(request):
    """
    Регистрация нового пользователя с аватаром.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('polls:index')
    else:
        form = SignUpForm()
    return render(request, 'polls/register.html', {'form': form})


@login_required
def profile(request):
    """
    Просмотр профиля пользователя.
    """
    return render(request, 'polls/profile.html', {'user': request.user})
