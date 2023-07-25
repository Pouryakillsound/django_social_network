from typing import Any
from django import http
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from .forms import UserRegisterForm, UserLoginForm, UserEditForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from .models import Relation, Profile
class UserRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    form_class = UserRegisterForm
    template_name = 'account/Register.html'
    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'You successfully created a new user', 'success')
            return redirect('home:home')
        return render(request, self.template_name,{'form':form})
    def get(self,request):
        form = self.form_class()
        return render(request, self.template_name,{'form':form})
    
class UserLoginView(View):
    def setup(self, request, *args, **kwags):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwags)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    form_class = UserLoginForm
    template_name = 'account/login.html'
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            username = cd.get('username')
            password = cd.get('password')
            user = authenticate(request,username=username,password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You logged in successfully', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            else:
                messages.error(request, 'oops,there is a problem with your password or username', 'danger')
        return render(request, self.template_name, {'form':form})
    def get(self,request):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})
    
class UserLogOutView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You should login first', 'warning')
            return redirect('account:login')
        return super().dispatch(request, *args, **kwargs)
    def get(self,request):
        logout(request)
        messages.success(request, 'You logged out', 'success')
        return redirect('home:home')
    
class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        is_followed = False
        relation = Relation.objects.filter(from_user = request.user, to_user = user_id)
        if relation.exists():
            is_followed = True
        user = User.objects.get(pk=user_id)
        posts = user.posts.all()
        return render(request, 'account/profile.html', {'user':user,'posts':posts, 'is_followed':is_followed})
    
class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = 'account/password_reset_email.html'

class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')

class UserPasswordCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'

class UserFollowView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        self.user_instance = User.objects.get(id=kwargs['user_id'])
        return super().setup(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        user = self.user_instance
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, 'You have already followed this user', 'danger')
            return redirect('account:profile', user.id)
        else:
            Relation.objects.create(from_user=request.user, to_user=self.user_instance).save()
            messages.success(request, 'You successfully followed this user', 'success')
            return redirect('account:profile', user.id)
        
class UserUnfollowView(LoginRequiredMixin, View):
    def setup(self, request, *args, **kwargs):
        self.user_instance = User.objects.get(id=kwargs['user_id'])
        return super().setup(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        relation = Relation.objects.filter(from_user=request.user, to_user=self.user_instance)
        if relation.exists():
            relation.delete()
            messages.success(request, 'You successfully unfollowed this user', 'success')
        else:
            messages.error(request, 'You have not followed this user, so you can not unfollow', 'danger')
        return redirect('account:profile', self.user_instance.id)
    
class UserEditView(LoginRequiredMixin, View):
    form_class = UserEditForm
    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email':request.user.email})
        return render(request, 'account/edit_user.html', {'form':form})
    
    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'You successfully udated your profile', 'success')
            return redirect('account:profile', request.user.id)