from odoo import models, api, fields

class SelectBidWizard(models.TransientModel):
    _name = 'select.bid.wizard'
    _description = 'Select Bid Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='RFQ', required=True)
    bid_id = fields.Many2one('vendor.bid', string='Selected Bid', required=True)

    def action_select_bid(self):
        self.ensure_one()
        self.purchase_order_id.write({
            'selected_bid_id': self.bid_id.id,
            'partner_id': self.bid_id.vendor_id.id,
        })
        self.bid_id.write({'state': 'selected'})
        self.purchase_order_id.vendor_bid_ids.filtered(lambda b: b.id != self.bid_id.id).write({'state': 'rejected'})
        for line in self.bid_id.line_ids:
            po_line = self.purchase_order_id.order_line.filtered(lambda l: l.product_id == line.product_id)
            if po_line:
                po_line.write({
                    'price_unit': line.price_unit,
                    'product_qty': line.quantity,
                })
        return {'type': 'ir.actions.act_window_close'}