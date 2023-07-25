from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
class Post(models.Model):
    body = models.TextField()
    slug = models.SlugField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    def __str__(self) -> str:
        return self.slug
    
    def get_absolute_url(self):
        return reverse('home:detail', args=[self.id, self.slug])
    

    class Meta:
        ordering = ('body',)


    def likes_count(self):
        return self.plikes.count()
    
    def can_like(self, user):
        user = user.ulikes.filter(post=self)
        if user.exists():
            return False
        return True
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ucomments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pcomments')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rcomments', null=True, blank=True)
    is_reply = models.BooleanField(default=False)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.body[:30]}'
    
    def get_absolute_url(self):
        return reverse('home:comment_delete', args=[self.id])
    
    class Meta:
        ordering = ['-created']

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ulikes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='plikes')