from odoo import models, fields, api
from odoo.exceptions import UserError


class VendorBid(models.Model):
    _name = 'vendor.bid'
    _description = 'Vendor Bid'

    purchase_order_id = fields.Many2one('purchase.order', string='RFQ', required=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    bid_date = fields.Date(string='Bid Date', default=fields.Date.today)
    total_amount = fields.Float(string='Total Bid Amount', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='purchase_order_id.currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('saved', 'Saved'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    line_ids = fields.One2many('vendor.bid.line', 'bid_id', string='Bid Lines')

    @api.depends('line_ids.price_subtotal')
    def _compute_total_amount(self):
        for bid in self:
            bid.total_amount = sum(bid.line_ids.mapped('price_subtotal'))
            
            
    def action_submit_bid(self):
        for bid in self:
            if not bid.line_ids:
                raise UserError("Cannot submit a bid without any bid lines.")
            bid.write({'state': 'saved'})
        return True

class VendorBidLine(models.Model):
    _name = 'vendor.bid.line'
    _description = 'Vendor Bid Line'

    bid_id = fields.Many2one('vendor.bid', string='Vendor Bid', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', required=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit