from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import markdown2
from . import util
from random import choice

class SearchForm(forms.Form):
    search = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Encyclopedia'}))

def index(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['search']
            if title.upper() in ( name.upper() for name in util.list_entries()):
                return render(request, "encyclopedia/entry.html", {
                    "title": title,
                    "newPage": markdown2.markdown(util.get_entry(title))
                })
            else:
                return render(request, "encyclopedia/results.html", {
                    "data": title,
                    "entries": util.list_entries()
                })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form" : SearchForm()
    })

def article(request, title):
    if title.upper() in ( name.upper() for name in util.list_entries()):
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "newPage": markdown2.markdown(util.get_entry(title))
        })
    elif title == 'new':
        return new(request)

    else:
        return render(request, "404.html", {
            "error": "There is no such entry"
        })

class NewEntry(forms.Form):
    title = forms.CharField( widget=forms.TextInput(attrs={'placeholder': 'Title', 'size': 97}))
    text = forms.CharField( widget=forms.Textarea(attrs={'placeholder': 'Add markdown','rows': 30,'cols': 90}))

class EditForm(forms.Form):
    text = forms.CharField( widget=forms.Textarea(attrs={'placeholder': 'Add markdown','rows': 30,'cols': 90}))

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["text"]
            with open(f"entries/{title}.md", "w") as f1:
                f1.write(content)
            return HttpResponseRedirect(reverse('article', kwargs={"title": title}))
    else:
        content = util.get_entry(title)
        form = EditForm({
            'text': content
        })
    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "title": title
    })

def new(request):
    if request.method == "POST":
        form = NewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            if title.upper() in (entry.upper() for entry in util.list_entries()):
                return render(request, "404.html", {
                    "error": "This entry has already existed"                  
                })
            util.save_entry(title, text)
            newPage = markdown2.markdown(util.get_entry(title))

            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "newPage": newPage
            })
    return render(request, "encyclopedia/new.html", {
        "form":  NewEntry()
    })

def random(request):
    rand = choice(util.list_entries()).upper()
    return HttpResponseRedirect(reverse('article', kwargs={"title": rand}))