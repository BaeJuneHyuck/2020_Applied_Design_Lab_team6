from team.models import Team
from django.contrib.postgres import search
from django.http import HttpResponse
from django.template import RequestContext
from django.urls import reverse
from django.views import generic
from django.utils import timezone


from user.models import User
from django.shortcuts import redirect, render, get_object_or_404
from .forms import PracticeCreateForm, CommentForm
from team.models import TeamInvitation
from practice.models import Practice, Comment, User
from django.conf import settings


class IndexView(generic.ListView):
    model = Practice
    template_name = 'practice/index.html'
    context_object_name = 'practices'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = Practice.objects.all()
        query = self.request.GET.get("qs", None)
        attribute = self.request.GET.get("attribute", None)
        if query is not None:
            if attribute == 'title':
                qs = qs.filter(title__icontains=query)
            elif attribute == 'author':
                qs = qs.filter(author__icontains=query)
            elif attribute == 'tier':
                qs = qs.filter(tier=query)
            elif attribute == 'text':
                qs = qs.filter(text__icontains=query)
        print(self.request.GET)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args,**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5  # Display only 5 page numbers
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range
        context['invitations']= TeamInvitation.objects.filter(invited_pk=self.request.user.pk).filter(checked=False)[:5]

        return context


class DetailView(generic.DetailView):
    model = Practice
    template_name = 'practice/detail.html'

    def comment(self, pk):
        practice = Practice.objects.get(pk=pk)
        comments = Comment.objects.filter(practice=practice)
        total_practice = Practice.total_practice()
        today = timezone.now().strftime("%Y-%m-%d")
        if self.method == 'POST':
            form = CommentForm(self.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = self.user
                comment.practice = practice
                comment.save()
            else:
                return HttpResponse('fail')
        else:
            form = CommentForm()

        form = CommentForm()

        return render(self, 'practice/detail.html', {'practice':practice, 'comments':comments, 'form':form,
                                                     'total_practice':total_practice, 'today':today})

class AttendView(generic.CreateView):
    model = Practice
    template_name = 'practice/attend.html'

    def get_object(self):
        return get_object_or_404(User, pk=self.request.comment_user.id)


class CreateView(generic.CreateView):
    login_url = settings.LOGIN_URL
    model = Practice

    def post_new(self):
        if not self.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, self.path))

        form = PracticeCreateForm(self.POST)
        if self.method == 'POST':
            form = PracticeCreateForm(self.POST)
            if form.is_valid():
                practice = form.save(commit=False)
                practice.author = self.user
                practice.save()
                return redirect(reverse('practice:index'))
            else:
                return render(self, 'practice/create.html', {'form': form})
        return render(self, 'practice/create.html', {'form': form})



