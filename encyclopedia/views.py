from django.shortcuts import render
from django import forms
from . import util
import markdown2
from django.urls import reverse
from django.http import HttpResponseRedirect
import random


class edit_form(forms.Form):

    title = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': 'readonly'}), label='')

    content = forms.CharField(widget=forms.Textarea, label='')


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    get = util.get_entry(entry)
    if get == None:
        return render(request, "encyclopedia/error.html")
    return render(request, "encyclopedia/entry.html", {
        "content": markdown2.markdown(get), "name": entry
    })


def search(request):
    key = request.GET.get('q', 0)
    get = util.get_entry(key)
    entries = util.list_entries()
    # if key==valid entry
    if get:
        return render(request, "encyclopedia/entry.html", {
            "content": markdown2.markdown(get), "name": key})
        # return HttpResponseRedirect(reverse("entry", kwargs={"entry": key}))

    # check if key is substring, if yes then put the entry that into a list
    else:
        list_ = []
        for entry in entries:
            if key.upper() in entry.upper():
                list_.append(entry)
        if list_:
            return render(request, "encyclopedia/index.html", {
                "entries": list_
            })
        else:
            return render(request, "encyclopedia/error.html")


def new_page(request):
    if request.method == 'POST':
        form = edit_form(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            # create markdown file and redirect to entry url
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
        else:
            return render(request, "encyclopedia/new_entry.html")

        if not form.is_valid():

            title = request.POST.get('title', 0)
            # if no title input
            if not title:
                return render(request, "encyclopedia/error.html")
            # if entry with the same name exists
            for entry in util.list_entries():
                if title == entry:
                    return render(request, "encyclopedia/error.html")

            # create markdown file and redirect to entry url
            util.save_entry(title, request.POST.get('content', 0))
            return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))

    else:
        return render(request, "encyclopedia/new_entry.html")


def edit(request, title):
    content = util.get_entry(title)
    form = edit_form(initial={'content': content, 'title': title})
    return render(request, "encyclopedia/new_entry.html", {'title': title, "form": form})


def random_entry(request):
    entries = util.list_entries()
    random_num = random.randint(0, len(entries)-1)
    title = entries[random_num]

    return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
