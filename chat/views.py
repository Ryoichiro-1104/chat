from django.shortcuts import render

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, resolve_url
from django.template.loader import render_to_string
from django.views import generic
from .forms import (
    LoginForm,UserCreateForm,UserUpdateForm
)
from .models import Room
from django.db.models import Q

# Create your views here.


def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        room = None
    if room is None:
        return render(request,'chat/room_notfound.html')
    return render(request, 'chat/room.html', {
        'room': room
    })

# def __str__(self)
#     return self.room_name

# def signup(request):
#     form = UserForm()
#     return render(request,'register/signup.html',{
#         'form': form
#     })

class Top(generic.TemplateView):
    template_name = 'register/login_top.html'

    def get(self, request, **kwargs):
        if not self.request.user.is_authenticated:
            return super().get(request, **kwargs)
        
        context = {}
        user = self.request.user
        rooms = Room.objects.filter(occupation=user.occupation)
        other_rooms=Room.objects.exclude(occupation=user.occupation)
        context['rooms'] = rooms
        context['other_rooms'] = other_rooms
        return render(request, 'register/login_top.html', context=context)
    #         template_name='chat/top.html'
    #     else:
    #         template_name='register/login_top.html'


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'
    redirect_authentic_user=True
    next='/'
    


class Logout(LogoutView):
    """ログアウトページ"""
    next_page = '/'

User = get_user_model()
...
...
...
class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        # subject = render_to_string('register/mail_template/create/subject.txt', context)
        # message = render_to_string('register/mail_template/create/message.txt', context)

        # user.email_user(subject, message)
        return redirect('chat:login')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = True
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        # subject = render_to_string('register/mail_template/create/subject.txt', context)
        # message = render_to_string('register/mail_template/create/message.txt', context)

        # user.email_user(subject, message)
        return redirect('chat:login')

# class UserCreateComplete(generic.TemplateView):
#     """メール内URLアクセス後のユーザー本登録"""
#     template_name = 'register/user_create_complete.html'
#     timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

#     def get(self, request, **kwargs):
#         """tokenが正しければ本登録."""
#         token = kwargs.get('token')
#         try:
#             user_pk = loads(token, max_age=self.timeout_seconds)

#         # 期限切れ
#         except SignatureExpired:
#             return HttpResponseBadRequest()

#         # tokenが間違っている
#         except BadSignature:
#             return HttpResponseBadRequest()

#         # tokenは問題なし
#         else:
#             try:
#                 user = User.objects.get(pk=user_pk)
#             except User.DoesNotExist:
#                 return HttpResponseBadRequest()
#             else:
#                 if not user.is_active:
#                     # 問題なければ本登録とする
#                     user.is_active = True
#                     user.save()
#                     return super().get(request, **kwargs)

#         return HttpResponseBadRequest()

class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True
     # 今ログインしてるユーザーのpkと、そのユーザー情報ページのpkが同じか、又はスーパーユーザーなら許可
    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'register/user_detail.html'


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'register/user_form.html'

    def get_success_url(self):
        return resolve_url('chat:user_detail', pk=self.kwargs['pk'])