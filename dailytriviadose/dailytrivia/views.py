from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import IntegrityError
from django.utils import timezone 
from datetime import timedelta
import json


from django.views.decorators.clickjacking import xframe_options_exempt

from .models import User, Trivia, TriviaGameRecord, UserTriviaDates



def index(request):
    user = request.user
    if request.path == '/bookmarked/' and user.is_authenticated:
        trivia_list = user.bookmarks.all()
    else:
        trivia_list = Trivia.objects.all()
    
    trivia_data = [
        {
            'trivia': trivia,
            'eligible_to_play': trivia.eligible_to_play(user) if user.is_authenticated else False,
            'has_won': trivia.has_won(user) if user.is_authenticated else False,
            'streak': get_trivia_streak(user, trivia) if user.is_authenticated else None,
        }
        for trivia in trivia_list
    ]
    if user.is_authenticated:
        sorted_trivia_data = sorted(
            trivia_data,
            key=lambda x: TriviaGameRecord.objects.get(user=user, trivia=x['trivia']).attempts,
            reverse = True
        )
        top_3_trivia = sorted_trivia_data[:3]
    else:
        top_3_trivia = []

    return render(request, 'dailytrivia/index.html', {
        'trivia_data': trivia_data,
        'top_3_trivia': top_3_trivia,
        })


def get_trivia_streak(user, trivia):
    trivia_dates, _ =UserTriviaDates.objects.get_or_create(user=user, trivia=trivia)
    streak = trivia_dates.calculate_streak()
    print(f"User {user.username} - Streak for {trivia.title}: {streak} ")

    return trivia_dates.calculate_streak()



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "dailytrivia/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "dailytrivia/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "dailytrivia/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "dailytrivia/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "dailytrivia/register.html")

@xframe_options_exempt
def trivia_detail(request, trivia_id):
    trivia = get_object_or_404(Trivia, id=trivia_id)
    return render(request, "dailytrivia/trivia_detail.html", {'trivia': trivia})



@login_required
def toggle_bookmark(request, trivia_id):
    try:
        trivia = Trivia.objects.get(id=trivia_id)

        if trivia in request.user.bookmarks.all():
            request.user.bookmarks.remove(trivia)
            is_bookmarked = False
        else:
            request.user.bookmarks.add(trivia)
            is_bookmarked = True
        return JsonResponse({'is_bookmarked': is_bookmarked})
    except:
        return HttpResponseNotFound("Trivia not found")


@login_required
def add_trivia(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        url = request.POST['url']
        embed_code = f'<iframe src="{url} width="600" height="400"></iframe>'
        reset_time = request.POST['reset_time']

        trivia = Trivia(title=title, description=description, url=url, embed_code=embed_code, reset_time=reset_time)
        trivia.save()

        return redirect('index')
    return render(request, 'dailytrivia/add_trivia.html')

@login_required
def create_or_update_trivia_record(request, trivia_id):
    if request.method == 'POST':
        user = request.user
        trivia = get_object_or_404(Trivia, id=trivia_id)
        played = request.POST.get("played") == 'true'
        won = request.POST.get("won") == 'true'
        type = request.POST.get('type')


        trivia_record, created = TriviaGameRecord.objects.get_or_create(
            user=user,
            trivia=trivia
        )
        if type == 'played':
            if trivia_record.has_reset_occurred():
                trivia_record.attempts += 1
                trivia_record.last_attempt_datetime = timezone.now()
                trivia_dates, _ = UserTriviaDates.objects.get_or_create(user=user, trivia=trivia)
                trivia_dates.add_attempt()
                streak = trivia_dates.calculate_streak()
                trivia_record.save()
                return JsonResponse({'success': True, 'created': created, 'streak': streak})
        elif type == 'won':
            if not trivia_record.has_win_occurred():
                trivia_record.wins += 1
                trivia_record.last_win_datetime = timezone.now()
                
                trivia_record.save()
            return JsonResponse({'success': True, 'created': created,})
        else:
            return JsonResponse({'success': False, 'message': 'You already played today.'}, status=400)
    return JsonResponse({'success': False, 'message': 'Not a post request.'}, status=400)


@login_required
def delete_trivia_attempt(request, trivia_id):
    if request.method == 'POST':
        user = request.user
        trivia = get_object_or_404(Trivia, id=trivia_id)

        type = request.POST.get('type')
        if type not in ['played', 'won']:
            return JsonResponse({'success': False, 'message': 'Type not found!'}, status=404)
        
        try:
            trivia_record = TriviaGameRecord.objects.get(user=user, trivia=trivia)
        except TriviaGameRecord.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'TriviaGameRecord not found.'}, status=404)
        if type == 'played':
            if not timezone.localtime(trivia_record.last_attempt_datetime).date() == timezone.localdate():
                return JsonResponse({'success': False, 'message': 'Cannot delete an attempt not made today'}, status=400)

            trivia_record.last_attempt_datetime = timezone.localtime(trivia_record.last_attempt_datetime) - timedelta(days=1)
            trivia_record.attempts -= 1
            trivia_record.save()
            
            try:
                trivia_dates = UserTriviaDates.objects.get(user=user, trivia=trivia)
                if timezone.datetime.fromisoformat(trivia_dates.play_dates[-1]).date() == timezone.localdate():
                    trivia_dates.play_dates.pop()
                    trivia_dates.save()
                # if timezone.localdate() in trivia_dates.play_dates:
                #     trivia_dates.play_dates.remove(timezone.localdate())
                #     trivia_dates.save()
            except:
                return JsonResponse({'success': False, 'message': 'Cannot find trivia dates.'}, status=400)
        elif type == 'won':
            if not timezone.localtime(trivia_record.last_win_datetime).date() == timezone.localdate():
                return JsonResponse({'success': False, 'message': 'Cannot delete a win not made today'}, status=400)
            trivia_record.last_win_datetime = timezone.localtime(trivia_record.last_win_datetime) - timedelta(days=1)
            trivia_record.wins -= 1
            trivia_record.save()
        return JsonResponse({'success': True, 'message': 'Attempt or win deleted successfully'})
    
    
    return JsonResponse({'success': False, 'message': 'Not a post request'}, status=400)


@login_required
def record_trivia_result(request):
    if request.method == "POST":
        user = request.user
        trivia_id = request.POST.get("trivia_id")
        played = request.POST.get("played")
        won = request.POST.get("won")

        try:
            trivia = Trivia.objects.get(id=trivia_id)
            today = timezone.now().date()
            current_time = timezone.now()
            record = TriviaGameRecord.objects.get_or_create(
                user=user,
                trivia=trivia,
            )
            reset_datetime = timezone.make_aware(
                timezone.datetime.combine(today, trivia.reset_time)
            )
            if record.last_attempt_datetime:
                last_attempt_time = record.last_attempt_datetime

                if last_attempt_time.date() == today:
                    if current_time < reset_datetime:
                        return JsonResponse({'success': False, 'message': 'You have already played today.'}, status=400)
            if played:
                record.attempt()
            if won:
                record.win()
            record.save()

            return JsonResponse({'success': True})
        except Trivia.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Trivia not found'}, status=400)
    return JsonResponse({'success': False}, status=400)



def profile(request, username):
    user = User.objects.get(username = username)
    user_trivia_dates = UserTriviaDates.objects.filter(user=user).exclude(play_dates=[])

    played_trivia_data = []
    for user_trivia in user_trivia_dates:
        trivia = user_trivia.trivia
        record = TriviaGameRecord.objects.filter(user=user, trivia=trivia).first()

        played_trivia_data.append({
            'trivia': trivia,
            'play_dates': user_trivia.play_dates,
            'streak': user_trivia.calculate_streak(),
            'best_streak': user_trivia.best_streak(),
            'attempts': record.attempts if record else 0,
            'wins': record.wins if record else 0,
        })


    return render(request, 'dailytrivia/profile.html', {
        'profile_user': user,
        'played_trivia_data': played_trivia_data,
    })