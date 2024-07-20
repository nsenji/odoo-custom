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

    vendor_ids = fields.Many2many(
        "res.partner",
        string="Vendor(s)",
        required=True,
        tracking=True,
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

    line_ids = fields.One2many("purchase.request.line", "request_id", string="Products")
    total_amount = fields.Float(
        string="Total Amount", compute="_compute_total_amount", store=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    description = fields.Text(string="Purpose")

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("purchase.request") or "New"
            )
        record = super().create(vals)
        record.message_subscribe([record.requester_id.partner_id.id])
        return record

    @api.depends("line_ids.subtotal")
    def _compute_total_amount(self):
        for request in self:
            request.total_amount = sum(request.line_ids.mapped("subtotal"))

    def action_make_request(self):
        if not self.line_ids:
            raise UserError("You cannot send an empty purchase request.")
        self.write({"state": "sent"})
        self.message_post(
            body="Purchase request sent to procurement department.",
            message_type="notification",
            subtype_xmlid="mail.mt_note",
        )

    def action_approve(self):
        self.write({"state": "approved"})
        self.message_post(
            body="Your purchase request has been approved.",
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=[self.requester_id.partner_id.id],
        )

    def action_create_rfq(self):
        self.ensure_one()
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']

        if not self.line_ids:
            raise UserError("Cannot create an RFQ without any product lines.")

        if not self.vendor_ids:
            raise UserError("Please select at least one vendor for the purchase request.")

        partner_id = self.vendor_ids[0].id

        po_vals = {
            'partner_id': partner_id,
            'vendor_ids': [(6, 0, self.vendor_ids.ids)], 
            'date_order': fields.Datetime.now(),
            'date_planned': self.date_required,
            'origin': self.name,
            'company_id': self.env.company.id,
            'currency_id': self.currency_id.id,
            'state': 'draft',
        }
        purchase_order = PurchaseOrder.create(po_vals)

        for line in self.line_ids:
            po_line_vals = {
                'order_id': purchase_order.id,
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.name,
                'product_qty': line.quantity,
                'product_uom': line.uom_id.id,
                'price_unit': line.price_unit,
                'date_planned': self.date_required,
            }
            PurchaseOrderLine.create(po_line_vals)

        self.write({'state': 'rfq_created'})

        # Return an action to view the created purchase order
        return {
            'name': 'Created RFQ',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_reject(self):
        self.write({"state": "rejected"})
        self.message_post(
            body="Your purchase request has been rejected.",
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=[self.requester_id.partner_id.id],
        )
