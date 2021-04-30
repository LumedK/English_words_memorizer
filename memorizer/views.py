from django.views import View
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from .models import Word, MemorizingList, MemorizingLine
from . import common
from django.http import HttpResponse


class CustomLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login.html'


class WordView(View):
    def get(self, request, pk=0, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login')
        user = request.user
        if pk == 0:
            word = Word(editor=user)
        else:
            word = Word.objects.get(pk=pk, editor=user)
        context = {
            'word': word,
        }
        return render(request, 'word.html', context=context)

    def post(self, request, pk=0, *args, **kwargs):
        if request.POST.get('save', None):
            properties = request.POST

            word, created = Word.objects.get_or_create(
                editor=request.user,
                eng_word=properties.get('eng_word', '')
            )
            word.editor = request.user
            word.eng_word = properties.get('eng_word', '')
            word.rus_word = properties.get('rus_word', '')
            word.transcription_uk = properties.get('transcription_uk', '')
            word.transcription_us = properties.get('transcription_us', '')
            word.save()
            return redirect('word', pk=word.pk)


class MemorizingListView(View):
    def get(self, request, pk=0, *args, **kwargs):
        pass
        if not request.user.is_authenticated:
            return redirect('/login')
        user = request.user
        if pk == 0:
            memorizing_list = MemorizingList(creator=user)
        else:
            memorizing_list = MemorizingList.objects.get(pk=pk, creator=user)
        memorizing_lines = MemorizingLine.objects.filter(link=memorizing_list).order_by('word')
        user_words = Word.objects.filter(editor=user)
        context = {
            'memorizing_list': memorizing_list,
            'memorizing_lines': memorizing_lines,
            'user_words': user_words,
        }
        return render(request, 'memorizing_list.html', context=context)



#         username = request.user.username
#         if pk == 0:
#             memory_list = MemoryList.objects.create()  # !kwargs
#         else:
#             memory_list = MemoryList.objects.get(pk=pk, username=username)
#         context = {}  # !context
#         return render(request, 'memorizing_list.html', context=context)


class DebugHomeView(View):
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('/login')

        user = request.user
        words = Word.objects.filter(editor=user)
        memorizing_lists = MemorizingList.objects.filter(creator=user)

        context = {
            'username': user.username,
            'memorizing_lists': memorizing_lists,
            'words': words,
        }
        return render(request, 'debug_home.html', context=context)






# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.views import LoginView
# from django.views import View
#
# from django.http import HttpResponse
# from .models import MemoryList
#
# from django.contrib.auth.models import User
#
#
# def user_from_request(request):
#     return User.objects.get(username=request.user.username)
#
#
# class CustomLoginView(LoginView):
#     redirect_authenticated_user = True
#     template_name = 'login.html'
#
#
# class HomeView(View):
#     def get(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('/login')
#         context = {'username': request.user.username,
#                    'lists': MemoryList.objects.filter(creator=user_from_request(request)),
#                    }
#         return render(request, 'home.html', context=context)
#
#
# class MemoryListView(View):
#     def get(self, request, pk=0, change='', *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('/login')
#         if pk == 0:
#             memory_list = MemoryList.objects().create(creator=request.user)
#             change = 'change'
#         else:
#             memory_list = get_object_or_404(MemoryList, pk=pk, creator=user_from_request(request))
#
#         context = {'username': request.user.username,
#                    'memory_list': memory_list,
#                    'change': bool(change)}
#         return render(request, 'memorize_list.html', context=context)
#         # return HttpResponse(f'{change}|{bool(change)}')
#
#     def post(self, request, pk=0, *args, **kwargs):
#
#         if request.POST.get('Change'):
#             return redirect('memory_list', pk, 'Change')
#
#         elif request.POST.get('Save'):
#             return HttpResponse('Save list')
#
#         elif request.POST.get('Cancel'):
#             return redirect('memory_list', pk)
#
#         elif request.POST.get('Run'):
#             return HttpResponse('Run list')
#
#         else:
#             return redirect('memory_list', pk)
#
#         # return HttpResponse(f"{kwargs.items()}")
#         # return HttpResponse(f"{request.POST.get('change')}")
#         # return HttpResponse(f'{list(request.POST.items())}')
#
#         # if request.POST.get('Change'):
#         #     return redirect(f'list/{request.pk}/change/')
#         # return redirect(f'list/{request.pk}/')
#         # return HttpResponse(f'{list(request.POST.items())}')
