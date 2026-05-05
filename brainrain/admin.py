from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.html import format_html, strip_tags
from .models import GameSession, StoryGame, Turn, Player
from .mixins import UserCreatorMixin
from unfold.admin import ModelAdmin
from scene.admin import AjaxSectionAdminMixin, AjaxTableSection
from unfold.admin import StackedInline
from unfold.sections import TemplateSection, render_to_string
from django.utils.safestring import mark_safe
from .sections import TableSection
import markdown

"""
height: fit-content;
flex-direction: column;
align-items: end;
line-height: 20px;
align-content: flex-e
"""

class PlayerInline(StackedInline):
    model = Player
    show_count = True  # This will run `count()`
    collapsible = True
    autocomplete_fields = ['user']

class EIPSection(TemplateSection):
    template_name = "sections/edit_inplace.html"

class PlayerTableSection(TableSection):
    model = Player
    
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    def scenes(self, obj):
        return f"{obj.turns.filter( type=GameSession.STATE_SCENE).count()}"
    
    def plots(self, obj):
        return f"{obj.turns.filter(type=GameSession.STATE_PLOT).count()}"
    
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    fields = ['username', 'scenes', 'plots']
    extra = 0
    show_count = True  # This will run `count()`
    collapsible = True
    related_name = 'players'

class PlayerStoryTableSection(TableSection):
    
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    fields = ['name', 'prompt']
    extra = 0
    show_count = True  # This will run `count()`
    collapsible = False
    related_name = 'story'

    def height(self, obj):
        return "230px"
    
class TurnTableSection(TableSection):
    template_name ="sections/turn.html"

    def context_data(self) -> dict:
        return {
            "session": self.instance,
            "player": self.request.user.players.filter(session=self.instance).first()
        }
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    def height(self, obj):
        return "230px"
    
    def prompt(self, obj):
        return mark_safe(markdown.markdown(obj.prompt))
    
    fields = ['player','prompt', 'type']
    extra = 0
    show_count = True  # This will run `count()`
    collapsible = False
    related_name = 'turns'

@admin.register(StoryGame)
class StoryGameAdmin(ModelAdmin):
    search_fields = ['name']
    
    def action_sessions(self, obj):
        return format_html("<a href='/admin/brainrain/session/?game__id__exact={0}'>{1} turns</a>", obj.id, obj.turn_set.count())

@admin.register(GameSession)
class GameSessionAdmin(ModelAdmin, UserCreatorMixin):
    class Media:
        js = ('js/section_ajax.js',)

    exclude = ('state',)
    inlines = [PlayerInline]
    autocomplete_fields = ['group']
    list_sections = [
        TurnTableSection,
        PlayerTableSection,
    ]
    list_display = ['game', 'state', 'turns_links']
    actions = ['create_user',]

    def turns_links(self, obj):
        return format_html("<a href='/admin/brainrain/turn/?session__id__exact={0}'>{1} turns</a>", obj.id, obj.turns.count())
    turns_links.short_description = "Turns"


@admin.register(Turn)
class TurnAdmin(ModelAdmin):
    
    fieldsets = (
        ("Idea",{
            "classes": ["tab"],
            "fields": ["prompt", ],
        }),
        ("Settings", {
            "classes": ["tab"],
            "fields": ["player", "session", "type", "prompt_refine"],
        }),
        ("Agent", {
            "classes": ["tab"],
            "fields": ["agent"],
        }),
    )

    @admin.display(description="Prompt")
    def my_prompt(self, obj):
        return mark_safe(f"<div class='markdown'>{markdown.markdown(obj.prompt)}</div>")
    
    list_display = ['player', 'my_prompt', ]
    list_filter = ['session',]

@admin.register(Player)
class PlayerAdmin(ModelAdmin):
    list_display = ['user', 'email']