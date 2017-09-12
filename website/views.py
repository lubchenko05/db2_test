from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from itertools import chain
from root.models import Profile, Post, PostLikes, Comment
from website.forms import UserRegistrationForm, UserLoginForm, VerifyEmailForm, SearchForm, PostCreateForm, \
    CommentCreateForm


def verify_required(f):
    def wrapper(*args, **kwargs):
        profile = Profile.objects.get(user=args[0].user)
        if not profile.verified_email:
            return redirect('verify')
        else:
            result = f(*args, **kwargs)
            return result
    return wrapper


def log_in(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=raw_password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Wrong email or password!')
                return render(request, 'website/signin.html', {'form': form})
        else:
                return render(request, 'website/signin.html', {'form': form})

    else:
            if request.user.is_authenticated():
                return redirect('home')
    form = UserLoginForm
    return render(request, 'website/signin.html', {'form': form})


@login_required(login_url='/login/')
def log_out(request):
    if request.method == 'GET':
        logout(request)
        return redirect('login')


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        if request.user.is_authenticated():
            return redirect('home')
        else:
            form = UserRegistrationForm
    return render(request, 'website/signup.html', {'form': form})


@login_required(login_url='/login/')
@verify_required
def home(request, order_by=None, search=None):
    fields = [str(i).split(".")[-1] for i in Post._meta.fields]
    if request.method == 'GET':
        form = SearchForm
        print(fields)
        if search and not order_by:
            post_list = Post.objects.filter(title__contains=search)
        elif order_by and not search:
            if order_by.lower() in fields:
                post_list = Post.objects.order_by(order_by)
            else:
                post_list = Post.objects.all()
        elif search and order_by:
            if order_by.lower() in fields:
                post_list = Post.objects.filter(title__contains=search).order_by(order_by)
            else:
                post_list = Post.objects.filter(title__contains=search)
        else:
            post_list = Post.objects.all()

        items = [(post, post.is_liked(request.user)) for post in post_list]
        paginator = Paginator(items, 10)
        pages = paginator.page_range
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        return render(request, 'website/home.html', {'posts': posts,
                                                     'form': form,
                                                     'pages': pages,
                                                     'search': search,
                                                     'fields': fields})
    elif request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search'].lower()
            post_list = Post.objects.filter(title__contains=search)
            items = [(post, post.is_liked(request.user)) for post in post_list]
            paginator = Paginator(items, 10)
            pages = paginator.page_range
            page = 1

            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            form = SearchForm
            return render(request, 'website/home.html', {'posts': posts,
                                                         'form': form,
                                                         'pages': pages,
                                                         'search': search,
                                                         'fields': fields})


@login_required(login_url='/login/')
def verify(request):
    if request.method == 'POST':
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            if str(profile.verified_code) == (form.cleaned_data.get('code')):
                profile.verified_email = True
                profile.save()
                return redirect('home')
            else:
                form.add_error(None, 'Wrong verification code!')
                return render(request, 'website/verify.html', {'form': form})
        else:
            return render(request, 'website/verify.html', {'form': form})
    else:
        profile = Profile.objects.get(user=request.user)
        if not profile.verified_email:
            form = VerifyEmailForm
            return render(request, 'website/verify.html', {'form': form})
        else:
            return redirect('home')


@login_required(login_url='/login/')
@verify_required
def like(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(pk=pk)
        if not PostLikes.objects.filter(user=request.user, post=post):
            post_like = PostLikes.objects.create(user=request.user, post=post)
            post_like.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/login/')
@verify_required
def dislike(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(pk=pk)
        post_likes = PostLikes.objects.filter(user=request.user, post=post)
        if post_likes:
            post_likes.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='/login/')
@verify_required
def about(request):
    if request.method == 'GET':
        return render(request, 'website/about.html')


@login_required(login_url='/login/')
@verify_required
def create_post(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            if request.FILES:
                post.image = request.FILES['image']
            post.save()
            return redirect('home')
        else:
            form.add_error(None, 'Wrong inputs!')
            return render(request, 'website/create_post.html', {'form': form})
    else:
            form = PostCreateForm
            return render(request, 'website/create_post.html', {'form': form})


@login_required(login_url='/login/')
@verify_required
def post_detail(request, pk):
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.owner = request.user
            comment.post = Post.objects.get(pk=pk)
            comment.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        post = Post.objects.get(pk=pk)
        comment = Comment.objects.filter(post=post)
        paginator = Paginator(comment, 10)
        pages = paginator.page_range
        page = request.GET.get('page')

        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
        form = CommentCreateForm
        return render(request, 'website/post_detail.html', {'form': form,
                                                            'post': post,
                                                            'liked': post.is_liked(request.user),
                                                            'comments': comments,
                                                            'page': pages})


