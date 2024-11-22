from django.db import models
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.utils import timezone
from datetime import timedelta, datetime

class User(AbstractUser):
    bookmarks = models.ManyToManyField('Trivia', blank=True, related_name='bookmarked_by')

    def __str__(self):
        return self.username

    def add_bookmark(self, trivia):
        self.bookmarks.add(trivia)
    
    def remove_bookmark(self, trivia):
        self.bookmarks.remove(trivia)

class Trivia(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField(max_length=500)
    embed_code = models.TextField(blank=True)
    allow_embed = models.BooleanField(default=True)
    reset_time = models.TimeField()
    color = models.CharField(max_length=7, default='#FFFFFF')
    image = models.URLField(max_length=500, default="https://png.pngtree.com/png-clipart/20210905/original/pngtree-trivia-poster-png-image_6706386.jpg")


    def __str__(self):
        return self.title
    
    def get_embed_code(self):
        if self.embed_code and self.allow_embed:
            return self.embed_code
        else:
            return f'<a href="{self.url}" target="_blank">Play {self.title}</a>'
    
    def eligible_to_play(self, user):
        if isinstance(user, AnonymousUser):
            return False
        record, created = TriviaGameRecord.objects.get_or_create(user=user, trivia=self)
        return record.has_reset_occurred()
    
    def attempt_count(self):
        return TriviaGameRecord.objects.filter(trivia=self).count()
        

class TriviaGameRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE)
    
    attempts = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    last_attempt_datetime = models.DateTimeField(null=True, blank=True)
    last_win_datetime = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} played {self.trivia.title}"

    def has_reset_occurred(self):
        now = timezone.now()
        reset_time_today = datetime.combine(now.date(), self.trivia.reset_time)
        
        # Convert to timezone-aware if necessary
        if timezone.is_aware(now):
            reset_time_today = timezone.make_aware(reset_time_today)

        # If last_attempt_datetime is None, it's the first attempt
        if not self.last_attempt_datetime:
            return True  # Eligible for a new attempt

        return self.last_attempt_datetime < reset_time_today
    
    def attempt(self):
        if self.has_reset_occurred():
            self.attempt += 1
            self.last_attempt_datetime = timezone.now
            self.save()
            
            trivia_dates, created = UserTriviaDates.objects.get_or_create(user=self.user, trivia=self.trivia)
            trivia_dates.add_attempt()

    def win(self):
        if self.has_reset_occurred():
            self.wins += 1
            self.last_attempt_datetime = timezone.now
            self.save()

    class Meta:
        unique_together = ('user', 'trivia')

class UserTriviaDates(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trivia = models.ForeignKey(Trivia, on_delete=models.CASCADE)
    play_dates = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user.username}'s streak on {self.trivia.title}"

    def add_attempt(self):
        today = timezone.now().date()

        if self.play_dates and self.play_dates[-1] == today.isoformat():
            return
        self.play_dates.append(today.isoformat())
        self.save()
    
    def calculate_streak(self):
        play_dates = [timezone.datetime.fromisoformat(date_str).date() for date_str in self.play_dates]

        if not play_dates:
            return 0
        

        today = timezone.now().date()

        last_play_date = play_dates[-1]

        if last_play_date != today and last_play_date != today - timedelta(days=1):
            return 0

        streak_count = 1
        previous_date = play_dates[-1]

        for date in reversed(play_dates[:-1]):
            if previous_date - date == timedelta(days=1):
                streak_count += 1
                previous_date = date
            else:
                break
        return streak_count
    
    def best_streak(self):
        if not self.play_dates:
            return 0
        
        play_dates = sorted([timezone.datetime.fromisoformat(date_str).date() for date_str in self.play_dates])

        best_streak = 0
        current_streak = 1

        for i in range(1, len(play_dates)):
            if play_dates[i] - play_dates[i-1] == timedelta(days=1):
                current_streak += 1
            else:
                best_streak = max(best_streak, current_streak)
                current_streak = 1

        best_streak = max(best_streak, current_streak)
        return best_streak
