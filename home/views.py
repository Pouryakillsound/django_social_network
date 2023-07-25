from typing import Any
from django import http
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Post, Comment, Like
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyCreateForm, SearchForm
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Count, F


class HomeView(View):
    form_class = SearchForm
    template_name = 'home/home.html'
    def get(self,request):
        posts = Post.objects.all()
        if request.GET.get('search'):
            posts = posts.filter(body__contains=request.GET['search'])
        return render(request, self.template_name, {'posts':posts, 'form':self.form_class})
    
class DetailView(View):
    form_class = CommentCreateForm
    def setup(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])
        self.comments = post.pcomments.filter(is_reply=False)
        return super().setup(request, *args, **kwargs)
    def get(self, request, post_id, post_slug):
        post = get_object_or_404(Post, pk=post_id, slug=post_slug)
        comments = self.comments
        can_like=False
        if request.user.is_authenticated and post.can_like(request.user):
            can_like = True
        return render(request, 'home/detail.html', {'post':post, 'comments':comments, 'form':self.form_class(), 'can_like':can_like})
    @method_decorator(login_required)
    def post(self, request, post_id, post_slug):
        post = Post.objects.get(pk=post_id, slug=post_slug)
        form = self.form_class(request.POST)
        comments = self.comments
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.save()
            return redirect('home:detail', post.id, post.slug)
        return render(request, 'home/detail.html', {'post':post, 'comments':comments, 'form':self.form_class()})



class  PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        if post.user == request.user:
            post.delete()
            messages.success(request, 'You successfully deleted this item', 'success')
        else:
            messages.error(request, 'You are not the creator of this post', 'danger')
        return redirect('home:home')
    

class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm
    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)
    def dispatch(self, request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['post_id'])
        if not request.user == post.user:
            messages.error(request, 'You are not creator of this item', 'success')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'form':form})
    
    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data.get('body')[:30])
            new_post.save()
            messages.success(request, 'You updated this item successfully', 'success')
            return redirect('home:detail', post.id, post.slug)
        
class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm
    def get(self, request):
        form = self.form_class()
        return render(request, 'home/create.html', {'form':form})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(request, 'You seccessfully created a new post', 'success')
            return redirect('home:home')
        
class CommentDeleteView(LoginRequiredMixin, View):
    def get(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        post = Post.objects.get(pk=comment.post.id)
        if comment.user == request.user:
            comment.delete()
            return redirect('home:detail', post.id, post.slug)
        return messages.error(request, 'This comment is not yours', 'danger')

class CommentReplyCreateView(LoginRequiredMixin, View):
    form_class = CommentReplyCreateForm
    template_name = 'home/reply.html'
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})
    
    def post(self,request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.reply = comment
            new_reply.post = post
            new_reply.user = request.user
            new_reply.is_reply = True
            new_reply.save()
        return redirect('home:detail', post.id, post.slug)
    
class LikeCreateView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        like = Like.objects.filter(user=user, post=post)
        if like.exists():
            messages.error(request, 'You have already liked this post', 'danger')
            return redirect('home:detail', post.id, post.slug)
        else:
            Like.objects.create(user=user, post=post)
            return redirect('home:detail', post.id, post.slug)


class LikeDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        like = Like.objects.filter(user=user, post=post)
        if not like.exists():
            messages.error(request, 'you havent liked this post yet', 'danger')
            return redirect('home:detail', post.id, post.slug)
        else:
            Like.objects.get(user=user, post=post).delete()
            return redirect('home:detail', post.id, post.slug)
        
class Test(View):
    def get(self, request):
        result = Post.objects.aggregate(Count('body'))
        print(result)
        return HttpResponse(f'Result:{result}')