from ads.models import Ad, Comment, Fav, Contact
from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from ads.forms import CreateForm, CommentForm

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.core.mail import send_mail
from django.conf import settings
from ads.forms import ContactForm
#from ads.contact import ContactForm

from ads.utils import dump_queries
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q

# class AdListView(OwnerListView):
#     model = Ad
#     template_name = "ads/ad_list.html"

#     def get(self, request) :
#         ad_list = Ad.objects.all()
#         favorites = list()
#         if request.user.is_authenticated:
#             # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
#             rows = request.user.favorite_ads.values('id')
#             # favorites = [2, 4, ...] using list comprehension
#             favorites = [ row['id'] for row in rows ]
#         ctx = {'ad_list' : ad_list, 'favorites': favorites}
#         return render(request, self.template_name, ctx)

class portfolioView(View):
    template_name = "ads/basic.html"

    def get(self, request):
        template_name = "ads/basic.html"
        return render(request, self.template_name)


class AdListView(View):
    template_name = "ads/ad_list.html"

    def get(self, request) :
        strval =  request.GET.get("search", False)

        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]

        if strval :
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(title__contains=strval)
            query.add(Q(text__contains=strval), Q.OR)
            objects = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 posts and watch the queries that happen
            objects = Ad.objects.all().order_by('-updated_at')[:10]
            # objects = Post.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'ad_list' : objects, 'favorites': favorites, 'search': strval}
        retval = render(request, self.template_name, ctx)

        dump_queries()
        return retval;


class ReqView(View):
    model = Ad
    success_url = reverse_lazy('ads:all')
    template_name = "ads/req.html"
    sub = "Request for login credentials"
    msg = "Thanks for contacting :)"
    msg += "\n"
    msg += "We will get back to as soon as possible !"
    from_email = settings.EMAIL_HOST_USER
    success_url = reverse_lazy('ads:all')
    to_email = [settings.EMAIL_HOST_USER]
    submitted = 0


    def get(self, request) :
        form = ContactForm()
        if 'submitted' in request.GET:
            submitted = 1
        else :
            submitted = 0
        ctx = {'form': form, 'submitted': submitted}
        return render(request, self.template_name, ctx)


    def post(self, request):
        form = ContactForm(request.POST)
        submitted = 0
        if form.is_valid():
            cd = form.cleaned_data
            items = Contact.objects.all()
            t = {'email': cd['email']}
            if t in items.values('email'):
                submitted = 2
                ctx = {'form': form, 'submitted': submitted}
                return render(request, self.template_name, ctx)
            else:
                form.save()
                # assert False
                m = "Credentials you want for your account -->"
                m += '\n' + "User Name : " + cd['username'] + '\n' + "Email : " + cd['email'] + '\n' + 'Password to set : ' + cd['password'] + '\n' + 'How do you know about me : ' + cd['source'] + '\n' + '\n' + '\n' + self.msg
                self.to_email.append(cd['email'])
                send_mail(self.sub, m, self.from_email, self.to_email, fail_silently=True)
            return HttpResponseRedirect('requestforlogin?submitted=True')
        else:
            ctx = {'form': form, 'submitted': submitted}
            return render(request, self.template_name, ctx)


class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ad_detail.html"
    def get(self, request, pk) :
        x = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'ad' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)


class AdCreateView(LoginRequiredMixin, View):
    # model = Ad
    # fields = ['title', 'price', 'text']
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')


    def get(self, request, pk=None) :
        form = CreateForm()
        ctx = { 'form': form }
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)

class AdUpdateView(LoginRequiredMixin, View):
    # model = Ad
    # fields = ['title', 'price', 'text']
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:all')


    def get(self, request, pk) :
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = { 'form': form }
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        pic = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)

class AdDeleteView(OwnerDeleteView):
    model = Ad


def stream_file(request, pk) :
    pic = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])


# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=t).delete()
        except Ad.DoesNotExist as e:
            pass

        return HttpResponse()

# class PicCreateView(LoginRequiredMixin, View):
#     template_name = 'pics/form.html'
#     success_url = reverse_lazy('pics:all')
#     def get(self, request, pk=None) :
#         form = CreateForm()
#         ctx = { 'form': form }
#         return render(request, self.template_name, ctx)

#     def post(self, request, pk=None) :
#         form = CreateForm(request.POST, request.FILES or None)

#         if not form.is_valid() :
#             ctx = {'form' : form}
#             return render(request, self.template_name, ctx)

#         # Add owner to the model before saving
#         pic = form.save(commit=False)
#         pic.owner = self.request.user
#         pic.save()
#         return redirect(self.success_url)

# class PicUpdateView(LoginRequiredMixin, View):
#     template_name = 'pics/form.html'
#     success_url = reverse_lazy('pics:all')
#     def get(self, request, pk) :
#         pic = get_object_or_404(Pic, id=pk, owner=self.request.user)
#         form = CreateForm(instance=pic)
#         ctx = { 'form': form }
#         return render(request, self.template_name, ctx)

#     def post(self, request, pk=None) :
#         pic = get_object_or_404(Pic, id=pk, owner=self.request.user)
#         form = CreateForm(request.POST, request.FILES or None, instance=pic)

#         if not form.is_valid() :
#             ctx = {'form' : form}
#             return render(request, self.template_name, ctx)

#         pic = form.save(commit=False)
#         pic.save()

#         return redirect(self.success_url)

# class PicDeleteView(OwnerDeleteView):
#     model = Pic
#     template_name = "pics/delete.html"
