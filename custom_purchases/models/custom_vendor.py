from odoo import models, fields

class Vendor(models.Model):
    _inherit = "res.partner"
    rfq_ids = fields.Many2many("purchase.order", string="RFQs")
