from odoo import models, fields, api


class PurchaseRequestLine(models.Model):
   _inherit = 'purchase.order.line'
   
   purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
   is_purchase_request = fields.Boolean(string='Is Purchase Request Line', default=False)