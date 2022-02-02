from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from itertools import chain
from django.db.models import CharField, Value

from .forms import FollowForm, ReviewForm, TicketForm
from .models import Ticket, Review, UserFollows


# Create your views here.

class UserMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def handle_no_permission(self):
        return HttpResponse(
            '<h1>Message: Only user who creates this ticket/review have access</h1>'
        )


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'home.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of reviews, tickets
        reviews = Review.objects.filter(user=self.request.user)
        reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
        tickets = Ticket.objects.filter(user=self.request.user)
        tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
        followers = UserFollows.objects.filter(user=self.request.user)
        my_followers = [follow.followed_user.username for follow in followers]
        users = User.objects.filter(username__in=my_followers)
        tickets_from_followers = Ticket.objects.filter(user__in=users)
        tickets_from_followers = tickets_from_followers.annotate(content_type=Value('TICKET_FROM_FOLLOWER',
                                                                                    CharField()))
        reviews_from_followers = Review.objects.filter(user__in=users)
        reviews_from_followers = reviews_from_followers.annotate(content_type=Value('REVIEW_FROM_FOLLOWER',
                                                                                    CharField()))

        # combine and sort the two types of posts
        context['posts'] = sorted(chain(reviews, tickets, reviews_from_followers, tickets_from_followers)
                                  , key=lambda post: post.time_created, reverse=True)
        # print(context)
        return context


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = ReviewForm
    template_name = 'review_detail.html'
    login_url = 'login'


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_new.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ReviewCreateView, self).form_valid(form)


    def get(self, request, *args, **kwargs):
        # review_form = self.reviewForm(**self.get_form_kwargs())
        review_form = ReviewForm
        ticket_form = TicketForm
        return render(request, 'review_new.html', {'review_form': review_form,
                                                   'ticket_form': ticket_form})

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            ticket_form = TicketForm(request.POST, request.FILES)
            if ticket_form.is_valid() and review_form.is_valid():
                ticket_form.instance.user = self.request.user
                ticket = ticket_form.save(commit=False)
                ticket.review_add = True
                ticket.save()
                review_form.instance.user = self.request.user
                review_form.instance.ticket = ticket
                review_form.save()
                return HttpResponseRedirect(reverse_lazy('home'))

            else:
                review_form = ReviewForm()
                ticket_form = TicketForm()
                return render(request, 'review_new.html', {'review_form': review_form,
                                                           'ticket_form': ticket_form})

            return HttpResponseRedirect(reverse_lazy('home'))


class ReviewTicketCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviewticket_new.html'
    login_url = 'login'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        review_form = ReviewForm()
        ticket = Ticket.objects.get(pk=self.kwargs.get('pk'))
        context = {'review_form': review_form, 'ticket': ticket}
        return render(request, 'reviewticket_new.html', context)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ReviewCreateView, self).form_valid(form)

    def post(self, request, pk):
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.ticket = get_object_or_404(Ticket, pk=pk)
                review.ticket.review_add = True
                review.ticket.save()
                review.save()
                return HttpResponseRedirect(reverse_lazy('home'))

        return render(request, 'reviewticket_new.html')


class ReviewUpdateView(UserMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_edit.html'
    # fields = ['headline', 'body', 'rating', ]
    login_url = 'login'
    success_url = reverse_lazy("home")

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def form_valid(self, form):
        form.instance.review = Review.objects.get(pk=self.kwargs.get('pk'))
        form.instance.user = self.request.user
        return super().form_valid(form)


class ReviewDeleteView(UserMixin, DeleteView):
    model = Review
    template_name = 'review_delete.html'
    success_url = reverse_lazy('home')
    login_url = 'login'


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'home.html'
    login_url = 'login'


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    context_object_name = 'ticket'
    template_name = 'ticket_detail.html'
    login_url = 'login'


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = 'ticket_new.html'
    fields = ['title', 'description', 'image']
    login_url = 'login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(UserMixin, UpdateView):
    model = Ticket
    template_name = 'ticket_edit.html'
    fields = ['title', 'description', 'image']
    login_url = 'login'


class TicketDeleteView(UserMixin, DeleteView):
    model = Ticket
    template_name = 'ticket_delete.html'
    success_url = reverse_lazy('home')
    login_url = 'login'


class PostView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "post.html"

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = Review.objects.filter(user=self.request.user)
        reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
        tickets = Ticket.objects.filter(user=self.request.user)
        tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
        context["posts"] = sorted(chain(reviews, tickets), key=lambda post: post.time_created,
                                  reverse=True)
        return context


class FollowerListView(LoginRequiredMixin, CreateView):
    form_class = FollowForm
    model = UserFollows
    template_name = 'follower_list.html'
    # login_url = 'login'
    success_url = reverse_lazy('follower_list')

    def get_form_kwargs(self):
        """ Passes the request object to the form class"""
        kwargs = super(FollowerListView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        get_followed_user = User.objects.get(username=form.cleaned_data["followed_user"])
        form.instance.followed_user = get_followed_user
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(FollowerListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all
        context['followers'] = UserFollows.objects.filter(user=self.request.user)
        context['users'] = UserFollows.objects.filter(followed_user=self.request.user)
        return context


class FollowerDeleteView(LoginRequiredMixin, DeleteView):
    model = UserFollows
    template_name = 'follower_delete.html'
    success_url = reverse_lazy('follower_list')
    login_url = 'login'
