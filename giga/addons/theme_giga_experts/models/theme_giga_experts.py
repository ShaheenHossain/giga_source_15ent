from giga import models


class ThemeGigaExperts(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_giga_experts_post_copy(self, mod):
        self.disable_view('website.template_header_default')
        self.disable_view('website.footer_custom')

        self.enable_view('website.template_header_contact')
        self.enable_view('website.template_footer_contact')
