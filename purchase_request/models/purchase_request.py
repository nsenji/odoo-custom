from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Request Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    requester_id = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="requester_id.department_id",
        store=True,
    )
    date_request = fields.Date(
        string="Request Date", default=fields.Date.context_today, tracking=True
    )
    date_required = fields.Date(string="Required Date", required=True, tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Request Sent"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("rfq_created", "RFQ created"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    line_ids = fields.One2many('purchase.request.line', 'request_id', string='Products')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    
    description = fields.Text(string='Description')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or 'New'
        record = super(PurchaseRequest, self).create(vals)
        record.message_subscribe([record.requester_id.partner_id.id])
        return record

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for request in self:
            request.total_amount = sum(request.line_ids.mapped('subtotal'))

    def action_make_request(self):
        if not self.line_ids:
            raise UserError("You cannot send an empty purchase request.")
        self.write({'state': 'sent'})
        self.message_post(
            body="Purchase request sent to procurement department.",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

    def action_approve(self):
        self.write({'state': 'approved'})
        self.message_post(
            body="Your purchase request has been approved.",
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=[self.requester_id.partner_id.id]
        )
        # TODO: Create RFQ logic here
        
    def action_create_rfq(self):
        
        # TODO: Create RFQ logic here
        self.write({'state': 'rfq_created'})

    def action_reject(self):
        self.write({'state': 'rejected'})
        self.message_post(
            body="Your purchase request has been rejected.",
            message_type='notification',
            subtype_xmlid='mail.mt_note',
            partner_ids=[self.requester_id.partner_id.id]
        )

    def action_add_product(self):
        self.ensure_one()
        return {
            'name': _('Add Product'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.request.line',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
            },
        }