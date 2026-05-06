from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.html import format_html, strip_tags
from .models import Session, Nudge, Theme, Turn, Participant
from .mixins import UserCreatorMixin
from unfold.admin import Any, HttpRequest, ModelAdmin
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

class ParticipantInline(StackedInline):
    model = Participant 
    show_count = True  # This will run `count()`
    collapsible = True
    autocomplete_fields = ['user']

class EIPSection(TemplateSection):
    template_name = "sections/edit_inplace.html"

class ParticipantTableSection(TableSection):
    model = Participant
    
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    def scenes(self, obj):
        turn_type = Session.STATE_SCENE
        turn_link = format_html("<a href='/admin/brainstorm/turn/?session__id__exact={0}&participant__id__exact={1}&type__exact=scene'>{2}</a>", obj.session.id, obj.id, obj.turns.filter(type=turn_type).count())
        if (obj.user == self.request.user):
            add_link = format_html("<a href='/admin/brainstorm/turn/add/?session={0}&participant={1}&type={2}'>[+]</a>", obj.session.id, obj.id, turn_type)
            turn_link = format_html("{} {}", turn_link, add_link)
        return mark_safe(turn_link)
    
    def plots(self, obj):
        turn_type = Session.STATE_PLOT
        turn_link = format_html("<a href='/admin/brainstorm/turn/?session__id__exact={0}&participant__id__exact={1}&type__exact=plot'>{2}</a>", obj.session.id, obj.id, obj.turns.filter(type=turn_type).count())
        if (obj.user == self.request.user):
            add_link = format_html("<a href='/admin/brainstorm/turn/add/?session={0}&participant={1}&type={2}'>[+]</a>", obj.session.id, obj.id, turn_type)
            turn_link = format_html("{} {}", turn_link, add_link)
        return mark_safe(turn_link)
    
    def nudges(self, obj):
        nudge_count = obj.user.received_nudges.count()
        nudge_link = format_html("<a href='/admin/brainstorm/nudge/?receiver__id__exact={0}'>{1}</a>", obj.user.id, nudge_count) 
        if (obj.user != self.request.user):
            add_link = format_html("<a href='/admin/brainstorm/nudge/add/?receiver={0}&session={1}&sender={2}'>-></a>", obj.user.id, obj.session.id, self.request.user.id)
            nudge_link = format_html("{} {}", nudge_link, add_link)
        return mark_safe(nudge_link)
    
    fields = ['username', 'scenes', 'plots', 'nudges']
    extra = 0
    show_count = True  # This will run `count()`
    collapsible = True
    related_name = 'participants'

class ParticipantStoryTableSection(TableSection):
    
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    fields = ['name', 'prompt']
    extra = 0
    show_count = True  # This will run `count()`
    collapsible = False
    related_name = 'story'

    def height(self, obj):
        return "230px"

class ThemeSection(TemplateSection):
    template_name ="sections/prompt.html"
    
    def get_context_data(self, request, instance) -> dict[str, Any]:
        return {
            "item" : instance.theme,
            "request": request,
        }


class TurnTableSection(TableSection):
    template_name ="sections/turn.html"

    def context_data(self) -> dict:
        return {
            "session": self.instance,
            "player": self.request.user.participants.filter(session=self.instance).first()
        }
    def name(self, obj):
        return f"{obj.user.username if obj.user else obj.email}"
    
    def height(self, obj):
        return "230px"

    def prompt(self, obj):
        return mark_safe(f"<div class='markdown'>{markdown.markdown(obj.prompt)}</div>")
    
    fields = ['participant','prompt', 'type']
    extra = 0
    show_count = True  # This will run `count()`
    collapsible = False
    related_name = 'turns'

@admin.register(Theme)
class ThemeAdmin(ModelAdmin):
    search_fields = ['name']
    
    def action_sessions(self, obj):
        return format_html("<a href='/admin/brainstorm/session/?theme__id__exact={0}'>{1} sessions</a>", obj.id, obj.sessions.count())

@admin.register(Session)
class SessionAdmin(ModelAdmin, UserCreatorMixin):
    class Media:
        js = ('js/section_ajax.js',)

    exclude = ('state',)
    inlines = [ParticipantInline]
    autocomplete_fields = ['group']
    list_sections = [
        ThemeSection,
        TurnTableSection,
        ParticipantTableSection,
    ]
    list_display = ['__str__', 'theme', 'state', 'turns_links']
    actions = ['create_user',]

    def turns_links(self, obj):
        return format_html("<a href='/admin/brainstorm/turn/?session__id__exact={0}'>{1} turns</a>", obj.id, obj.turns.count())
    turns_links.short_description = "Turns"


@admin.register(Turn)
class TurnAdmin(ModelAdmin):
    
    fieldsets = (
        ("Write",{
            "classes": ["tab"],
            "fields": ["prompt", ],
        }),
        ("Settings", {
            "classes": ["tab"],
            "fields": ["participant", "session", "type", "prompt_refine", "agent"],
        })
    )

    @admin.display(description="Prompt")
    def my_prompt(self, obj):
        return mark_safe(f"<div class='markdown'>{markdown.markdown(obj.prompt)}</div>")
    
    list_display = ['id', 'participant',  'my_prompt', 'session' ]
    list_filter = ['session',]

@admin.register(Participant)
class ParticipantAdmin(ModelAdmin):
    list_display = ['user', 'email']

@admin.register(Nudge)
class NudgeAdmin(ModelAdmin):
    list_display = ["id", 'sender', 'receiver', 'session', 'message']
    fieldsets = (
        ("Write",{
            "classes": ["tab"],
            "fields": ["message", ],
        }),
        ("Settings", {
            "classes": ["tab"],
            "fields": ["receiver", "sender", "session"],
        })
    )