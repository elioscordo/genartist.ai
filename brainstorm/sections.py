from typing import Any

from django.contrib.admin.utils import label_for_field, lookup_field
from django.db.models import Model
from django.http import HttpRequest
from django.template.loader import render_to_string

from unfold.utils import display_for_field
from unfold.sections import BaseSection, TemplateSection

class TableSection(BaseSection):
    fields = []
    related_name = None
    verbose_name = None
    height = None
    template_name ="unfold/components/table.html"

    def context_data(self) -> dict:
        return {}
    
    def render(self) -> str:
        if self.related_name is None:
            raise ValueError("TableSection must have a related_name")

        results = getattr(self.instance, self.related_name)
        headers = []
        rows = []

        for field_name in self.fields:
            if hasattr(self, field_name):
                if hasattr(getattr(self, field_name), "short_description"):
                    headers.append(getattr(self, field_name).short_description)
                else:
                    headers.append(field_name)
            else:
                headers.append(label_for_field(field_name, results.model))

        for result in results.all():
            row = []

            for field_name in self.fields:
                if hasattr(self, field_name):
                    row.append(getattr(self, field_name)(result))
                else:
                    field, attr, value = lookup_field(field_name, result)
                    row.append(display_for_field(value, field, "-"))

            rows.append(row)

        context = {
            "request": self.request,
            "table": {
                "headers": headers,
                "rows": rows,
            },
        }
        context.update(self.context_data())
        if hasattr(self, "verbose_name") and self.verbose_name:
            context["title"] = self.verbose_name

        if hasattr(self, "height") and self.height:
            context["height"] = self.height

        return render_to_string(
            self.template_name,
            context=context,
        )