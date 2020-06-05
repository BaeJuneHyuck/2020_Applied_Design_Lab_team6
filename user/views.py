from django.views.generic import CreateView, DetailView

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from user.forms import UserRegistrationForm, LoginForm, UserMypageForm
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.views import generic
# email 발송
from django.contrib.auth.tokens import default_token_generator
from esportsPlatform import settings
from django.views.generic import CreateView, FormView
from .mixins import VerifyEmailMixin
from .forms import VerificationEmailForm
from .models import User, lol_record
from team.models import TeamInvitation

class UserRegistrationView(VerifyEmailMixin, CreateView):
    template_name = 'user/user_model.html'
    model = get_user_model()
    form_class = UserRegistrationForm
    success_url = '/user/login/'
    verify_url = '/user/verify/'

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance:
            self.send_verification_email(form.instance)
        return response


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'user/login_form.html'

    def form_invalid(self, form):
        messages.error(self.request, '로그인에 실패하였습니다.', extra_tags='danger')
        return super().form_invalid(form)


class UserMypageView(UpdateView):
    model = get_user_model()
    template_name = 'user/mypage.html'
    form_class= UserMypageForm

    def get(self, request):
        form = UserMypageForm(instance=request.user)
        lolid = self.model.objects.get(pk = request.user.pk)
        records = lol_record.objects.filter(nickName = lolid.lolid)
        invitations= TeamInvitation.objects.filter(invited_pk=request.user.pk).filter(checked=False)[:5]

        args = {'form': form, 'records':records, 'invitations':invitations}

        return render(request, self.template_name, args)

    def post(self, request):
        form = UserMypageForm(request.POST, instance=request.user)
        lolid = self.model.objects.get(pk=1)
        records = lol_record.objects.filter(nickName= lolid.lolid)
        invitations= TeamInvitation.objects.filter(invited_pk=request.user.pk).filter(checked=False)[:5]
        if form.is_valid():
            form.save()
            return redirect('/user/mypage/')

        args = {'form': form, 'records':records, 'invitations':invitations}
        return render(request, self.template_name, args)


class UserVerificationView(TemplateView):

    model = get_user_model()
    redirect_url = '/user/login/'
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        if self.is_valid_token(**kwargs):
            messages.info(request, '인증이 완료되었습니다.')
        else:
            messages.error(request, '인증이 실패되었습니다.')
        return HttpResponseRedirect(self.redirect_url)   # 인증 성공여부와 상관없이 무조건 로그인 페이지로 이동

    def is_valid_token(self, **kwargs):
        pk = kwargs.get('pk')
        token = kwargs.get('token')
        user = self.model.objects.get(pk=pk)
        is_valid = self.token_generator.check_token(user, token)
        if is_valid:
            user.is_active = True
            user.save()     # 데이터가 변경되면 반드시 save() 메소드 호출
        return is_valid


class ResendVerifyEmailView(VerifyEmailMixin, FormView):
    model = get_user_model()
    form_class = VerificationEmailForm
    success_url = '/user/login/'
    template_name = 'user/resend_verify_email.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            messages.error(self.request, '알 수 없는 사용자 입니다.')
        else:
            self.send_verification_email(user)
        return super().form_valid(form)

