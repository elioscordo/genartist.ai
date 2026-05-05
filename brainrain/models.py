from django.db import models
from django.contrib.auth.models import User
            

class StoryGame(models.Model):
    name = models.CharField(max_length=100, default='New Game')
    prompt = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return "{}".format(self.name)


class GameSession(models.Model):
    game = models.ForeignKey('StoryGame', on_delete=models.CASCADE, null=True, blank=True)
    story = models.ForeignKey('scene.Story', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('scene.StoryGroup', help_text="If the invitation is accepted the user will also be added to this group. You can generate invitations for group members automatically",  on_delete=models.CASCADE, null=True, blank=True)
    turn_duration = models.DurationField(null=True, blank=True, help_text ="Duration of each turn. After this time, the turn will be automatically finished. Format: HH:MM:SS (e.g. 00:30:00 for 30 minutes)")
    agent = models.ForeignKey('agent.Agent', on_delete=models.CASCADE, null=True, blank=True)

    STATE_CREATED = 'created' 
    STATE_READY = 'ready'
    STATE_SCENE = 'scene'
    STATE_PLOT = 'plot'   
    STATE_FINISHED = 'finished'
    
    STATES = [
        (STATE_CREATED, 'Created'),
        (STATE_READY, 'Ready'),
        (STATE_SCENE, 'Hints'),
        (STATE_PLOT, 'Plots'),
        (STATE_FINISHED, 'Finished')
    ]
    state = models.CharField(max_length=100, choices=STATES, default=STATE_READY)

    def __str__(self):
        return "{}".format(self.game.name)
    def turn_type(self):
        if self.state in [self.STATE_SCENE, self.STATE_PLOT]:
            return self.state
        return self.STATE_SCENE
    
    def should_play(self, player, turn_type):
        if self.state != turn_type:
            raise ValueError("It's not the correct turn type. Current state: {}".format(self.state))
        turns = self.turn_set.filter(type=type).order_by('-id')
        if turns.count() != player.order:
            raise ValueError("It's not  {}'s turn. It should be {}'s turn.".format(self.state, player.order))
        last_turn = turns.first()
        return last_turn.finished if last_turn else True


class Player(models.Model):
    session = models.ForeignKey('GameSession', related_name='players', on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField(default=0)
    user = models.ForeignKey('auth.User', related_name='players', on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.email and not self.user:
            raise ValueError("Either email or user must be provided.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.user.username)

    def username(self):
        return self.user.username if self.user else self.email

class Turn(models.Model):
    TYPE_HELP = 'help'
    TURN_TYPES = [
        (GameSession.STATE_SCENE, 'Add Scene'),
        (GameSession.STATE_PLOT, 'Plots'),
        (TYPE_HELP, 'Help')
    ]

    type = models.CharField(max_length=100, choices=TURN_TYPES, default=GameSession.STATE_SCENE)
    prompt = models.TextField(null=True, blank=True)
    prompt_refine = models.TextField(null=True, blank=True)
    session = models.ForeignKey('GameSession', related_name='turns', on_delete=models.CASCADE, null=True, blank=True)
    player = models.ForeignKey('Player', related_name='turns', on_delete=models.CASCADE, null=True, blank=True)
    agent = models.ForeignKey('agent.Agent', on_delete=models.CASCADE, null=True, blank=True)
    pass_turn = models.BooleanField(default=False, help_text="If true, the turn will be passed to the next player")
    
    def __str__(self):
        return "{}".format(self.player.user.username)

"""    def save(self, *args, **kwargs):
        if not self.game and self.player:
            self.game = self.player.game
        if self.session and self.session.state == GameSession.STATE_FINISHED:
            raise ValueError("Cannot add turns to a finished game.")
        self.session.should_play(self.player, self.type)
        super().save(*args, **kwargs)
"""

     