from django.views import View
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from .models import Word, MemorizingList, MemorizingLine, Statistics, User
import re
import json
from django.db.models import Min
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

    def get_response(self, request, memorizing_list, memorizing_lines):
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')
        if not isinstance(memorizing_list, MemorizingList):
            return HttpResponse('Memorizing list not found')

        user_words = Word.objects.filter(editor=user).order_by('eng_word', 'rus_word')
        context = {
            'memorizing_list': memorizing_list,
            'memorizing_lines': memorizing_lines,
            'user_words': user_words,
        }
        return render(request, 'memorizing_list.html', context=context)

    def get(self, request, pk=0, *args, **kwargs):
        user = request.user
        if pk == 0:
            memorizing_list = MemorizingList(creator=user)
        else:
            memorizing_list = MemorizingList.objects.get(pk=pk, creator=user)

        memorizing_lines = MemorizingLine.objects.filter(link=memorizing_list).order_by('word')
        return self.get_response(request, memorizing_list, memorizing_lines)

    def post(self, request, pk=0, *args, **kwargs):
        def get_added_lines(properties, memorizing_list):

            word_pk_list = [
                int(v) for k, v in properties.items() if re.match("^added_line[0-9]+$", k)
            ]

            user_words = Word.objects.filter(
                editor=request.user,
                pk__in=word_pk_list
            )
            available_words = dict((word.pk, word) for word in user_words)

            lines = [
                MemorizingLine(link=memorizing_list, word=available_words[word_pk])
                for word_pk in word_pk_list if word_pk in available_words.keys()
            ]
            return lines

        properties = request.POST
        memorizing_list = MemorizingList(
            completed=properties.get('memorizing_list_completed', None) == 'on',
            creator=request.user,
            name=properties.get('memorizing_list_name', None),
        )
        lines = get_added_lines(properties, memorizing_list)

        if not memorizing_list.name:
            default_list_name = ', '.join([line.word.eng_word for line in lines])[:25]
            default_list_name = f'{default_list_name[:22]}...' if len(default_list_name) > 25 else default_list_name
            memorizing_list.name = default_list_name

        if properties.get('add', None):
            word_pk = int(properties.get('new_line', '0'))
            available_words = Word.objects.filter(editor=request.user, pk=word_pk)
            if len(available_words) != 0:
                new_word = available_words[0]
                new_line = MemorizingLine(link=memorizing_list, word=new_word)
                lines.append(new_line)

        elif properties.get('remove', None):
            remove_index = int(properties.get('remove', '0')) - 1
            if 0 <= remove_index <= len(lines):
                lines.pop(remove_index)

        elif properties.get('save', None):
            lists = MemorizingList.objects.filter(pk=pk, creator=request.user)
            if lists:
                memory_list_for_update = lists[0]
            else:
                memory_list_for_update = MemorizingList()
            memory_list_for_update.completed = memorizing_list.completed
            memory_list_for_update.creator = memorizing_list.creator
            memory_list_for_update.name = memorizing_list.name
            memory_list_for_update.save()

            old_lines = MemorizingLine.objects.filter(link=memory_list_for_update).delete()
            MemorizingLine.objects.bulk_create(
                [MemorizingLine(link=memory_list_for_update, word=line.word) for line in lines])
            return redirect('memorizing_list', pk=memory_list_for_update.pk)

        elif properties.get('run'):
            return redirect('run_list', pk)

        return self.get_response(request, memorizing_list, lines)


class DebugHomeView(View):
    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('/login')

        user = request.user
        words = Word.objects.filter(editor=user).order_by('eng_word', 'rus_word')
        memorizing_lists = MemorizingList.objects.filter(creator=user).order_by('name')

        context = {
            'username': user.username,
            'memorizing_lists': memorizing_lists,
            'words': words,
        }
        return render(request, 'debug_home.html', context=context)


class RunListView(View):
    class RunProgress:
        def __init__(self, request=None, list_pk=None, lines=None, progress_json=None):
            self.user_pk = None
            self.list_pk = None
            self.lines_pk = None
            self.run_number = None
            self.current_index = None
            self.user_input_list = None
            if progress_json is None:
                self.user_pk = request.user.pk
                self.list_pk = list_pk
                self.lines_pk = [line.pk for line in lines]
                self.run_number = self.get_new_run_number(request.user)
                self.current_index = 0
            else:
                (
                    self.user_pk,
                    self.list_pk,
                    self.lines_pk,
                    self.run_number,
                    self.current_index,
                ) = self.from_json(progress_json)

        def get_new_run_number(self, user):
            memorizing_list = MemorizingList.objects.get(creator=user, pk=self.list_pk)

            last_run_selection = Statistics.objects.filter(
                user=user,
                list=memorizing_list,
            ).order_by('-run')[:1]
            last_run = last_run_selection[0].run if last_run_selection else 0
            last_run_completed_selection = Statistics.objects.filter(
                user=user,
                list=memorizing_list,
                run=last_run,
            ).aggregate(Min('completed'))
            run_completed = bool(last_run_completed_selection['completed__min'])
            run_number = last_run + 1 if run_completed else last_run
            return run_number

        def get_context(self):
            user = User.objects.get(pk=self.user_pk)
            memorizing_list = MemorizingList.objects.get(pk=self.list_pk)
            statistics = Statistics.objects.filter(
                user=user,
                list=memorizing_list,
                run=self.run_number,
            )
            list_statistics = dict((stat.line.pk, stat) for stat in statistics)
            progress = []
            for line_pk in self.lines_pk:
                element = list_statistics.get(line_pk, None)
                if not element:
                    current_line = MemorizingLine.objects.get(pk=line_pk)
                    element = Statistics.objects.create(
                        user=user,
                        list=memorizing_list,
                        line=current_line,
                        word=current_line.word,
                        run=self.run_number,
                    )
                progress.append(element)
            return progress

        def to_json(self):
            return json.dumps(self, default=lambda o: o.__dict__)

        def from_json(self, progress_json):
            decoded = json.loads(progress_json)
            return (
                decoded['user_pk'],
                decoded['list_pk'],
                decoded['lines_pk'],
                decoded['run_number'],
                decoded['current_index']
            )

    def render_run_template(self, request, list_pk, progress=None):
        if not request.user.is_authenticated:
            return redirect('/login')
        if progress is None:
            lines = MemorizingLine.objects.filter(link__pk__exact=list_pk)
            progress = RunListView.RunProgress(request=request, list_pk=list_pk, lines=lines)
        progress_context = progress.get_context()
        if len(progress_context) == 0:
            return HttpResponse('The list is empty')
        current_progress = progress_context[progress.current_index]
        context = {
            'progress': progress_context,
            'progress_json': progress.to_json,
            'current_progress': current_progress,
        }
        return render(request, 'run_list.html', context=context)

    def get(self, request, list_pk, *args, **kwargs):
        available_list = MemorizingList.objects.filter(creator=request.user, pk=list_pk)[:1]
        if not available_list:
            return HttpResponse('This list is not available or does not exist')
        return self.render_run_template(request, list_pk)

    def post(self, request, list_pk, *args, **kwargs):
        properties = request.POST
        progress = RunListView.RunProgress(progress_json=properties.get('progress_json'))
        user = request.user
        if properties.get('check', None):
            current_line_pk = progress.lines_pk[progress.current_index]
            current_stats = Statistics.objects.get(
                line__pk=current_line_pk,
                run=progress.run_number
            )
            check_word = properties.get('check_field', '')
            correct = current_stats.word.eng_word.lower() == check_word.lower()
            if not correct:
                current_stats.failed += 1
            current_stats.completed += 1
            current_stats.user_text = check_word
            current_stats.save()

        elif properties.get('next', None):
            max_index = len(progress.lines_pk) - 1
            next_index = progress.current_index + 1
            next_index = min(next_index, max_index)
            progress.current_index = next_index

        elif properties.get('previous', None):
            pre_index = progress.current_index - 1
            pre_index = max(pre_index, 0)
            progress.current_index = pre_index

        return self.render_run_template(request, list_pk, progress)


class DeleteContextView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('/login')

        lists = MemorizingList.objects.filter(creator=user)
        words = Word.objects.filter(editor=user)
        context = {
            'lists': lists,
            'words': words,
        }
        return render(request, 'delete_list.html', context=context)

    def post(self, request, *args, **kwargs):
        properties = request.POST
        if properties.get('delete_marked', None):

            list_pk_to_del = [
                int(v) for k, v in properties.items() if re.match("^list_[0-9]+$", k)
            ]
            word_pk_to_del = [
                int(v) for k, v in properties.items() if re.match("^word_[0-9]+$", k)
            ]

            user_lists = MemorizingList.objects.filter(
                creator=request.user,
                pk__in=list_pk_to_del
            ).delete()
            user_words = Word.objects.filter(
                editor=request.user,
                pk__in=word_pk_to_del
            ).delete()
        return redirect('delete_context')
