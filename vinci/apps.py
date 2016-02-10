from django.apps import AppConfig

class VinciConfig(AppConfig):
    name = 'vinci'
    verbose_name = "Vinci"

    def ready(self):
        from django.conf import settings
        from django.template import Template
        from vinci.utils import load_modes, load_template_for_mode

        # Load modes
        modes = load_modes(settings.VINCI_MODE_LIST, settings.VINCI_MODE_TEMPLATE_BASE)
        settings.VINCI_MODES = modes

        # Load the edit-mode HTML
        filename = '{}/vinci/templates/partials/_edit_mode.html'.format(settings.BASE_DIR)

        with open(filename, 'r') as f:
            settings.VINCI_EDIT_MODE_HTML = f.read()

        # Load the entry start HTML
        filename = '{}/vinci/templates/partials/_entry_start.html'.format(settings.BASE_DIR)

        with open(filename, 'r') as f:
            settings.VINCI_ENTRY_START_HTML = f.read()

        # Load the entry end HTML
        filename = '{}/vinci/templates/partials/_entry_end.html'.format(settings.BASE_DIR)

        with open(filename, 'r') as f:
            settings.VINCI_ENTRY_END_HTML = f.read()

        # Load templates for modes
        settings.VINCI_TEMPLATES = {}
        for key in settings.VINCI_MODES:
            # Load templates
            list_template = load_template_for_mode('list', key)
            detail_template = load_template_for_mode('detail', key)
            search_template = load_template_for_mode('search', key)

            settings.VINCI_TEMPLATES[key] = {
                'list': Template(list_template),
                'detail': Template(detail_template),
                'search': Template(search_template),
            }

        pass # startup code here
