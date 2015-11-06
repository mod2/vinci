from django.conf import settings
from django.apps import AppConfig
from django.template import Template

from vinci.utils import load_modes, load_template_for_mode

class VinciConfig(AppConfig):
    name = 'vinci'
    verbose_name = "Vinci"
    def ready(self):
        # Load modes
        modes = load_modes(settings.VINCI_MODES, settings.VINCI_MODE_TEMPLATE_BASE)
        settings.VINCI_MODES = modes

        # Load templates for modes
        settings.VINCI_TEMPLATES = {}
        for key in settings.VINCI_MODES:
            # Load templates
            list_template = load_template_for_mode('list', key)
            detail_template = load_template_for_mode('detail', key)

            settings.VINCI_TEMPLATES[key] = {
                'list': Template(list_template),
                'detail': Template(detail_template),
            }

        pass # startup code here
