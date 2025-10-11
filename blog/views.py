from django.shortcuts import render, get_object_or_404
from .models import Post

def index(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/index.html', {'posts': posts})

def post_detail(request, slug):
    p = get_object_or_404(Post, slug=slug, published=True)
    return render(request, 'blog/detail.html', {'post': p})
