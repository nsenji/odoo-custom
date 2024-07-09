from odoo import models, api

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def send_rfq_to_multiple_vendors(self, composer_vals, vendor_ids):
        for vendor_id in vendor_ids:
            composer_vals['partner_ids'] = [(6, 0, [vendor_id])]
            composer = self.create(composer_vals)
            composer.send_mail()
        return True

    def send_mail(self, auto_commit=False):
        if self._context.get('vendor_ids'):
            for res_id in self._context.get('active_ids', []):
                composer_values = self.copy_data()[0]
                composer_values['res_id'] = res_id
                self.send_rfq_to_multiple_vendors(composer_values, self._context['vendor_ids'])
            return True
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)