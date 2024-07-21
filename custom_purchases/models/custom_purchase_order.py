from odoo import models, fields
from odoo.exceptions import UserError
from odoo import api, fields, models, _

from odoo.exceptions import UserError


class CustomPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vendor_ids = fields.Many2many(
        "res.partner",
        string="Vendor(s)",
        required=True,
        domain=[("supplier_rank", ">", 0)],
        tracking=True,
        check_company=True,
    )
   
    vendor_bid_ids = fields.One2many('vendor.bid', 'purchase_order_id', string='Vendor Bids')
    selected_bid_id = fields.Many2one('res.partner', string='Best Bid')
    state = fields.Selection(selection_add=[('bid_selection', 'Bid Selection')])

    

    def button_confirm(self):
        if not self.selected_bid_id:
            raise UserError("Please select the best bid first")
        
        for order in self:
            if order.state not in ["draft", "sent", "bid_selection"]:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({"state": "to approve"})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    @api.onchange("vendor_ids")
    def onchange_vendor_ids(self):
        if self.vendor_ids:
            self.partner_id = self.vendor_ids[:1].id
            self.fiscal_position_id = self.env[
                "account.fiscal.position"
            ]._get_fiscal_position(self.vendor_ids[:1])
            self.payment_term_id = self.vendor_ids[
                :1
            ].property_supplier_payment_term_id.id
            self.currency_id = (
                self.vendor_ids[:1].property_purchase_currency_id.id
                or self.env.company.currency_id.id
            )
        else:
            self.fiscal_position_id = False
            self.payment_term_id = False
            self.currency_id = self.env.company.currency_id.id

    def action_rfq_send(self):
        self.ensure_one()
        if not self.vendor_ids:
            raise UserError(_("Please select at least one vendor."))

        ir_model_data = self.env["ir.model.data"]

        try:
            if self.env.context.get("send_rfq", False):
                template_id = ir_model_data._xmlid_lookup(
                    "custom_purchases.email_template_edi_purchase_custom"
                )[1]
            else:
                template_id = ir_model_data._xmlid_lookup(
                    "purchase.email_template_edi_purchase_done"
                )[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                "mail.email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False

        ctx = dict(self.env.context or {})
        ctx.update(
            {
                "default_model": "purchase.order",
                "default_res_ids": self.ids,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
                "force_email": True,
                "mark_rfq_as_sent": True,
                "vendor_ids": self.vendor_ids.ids,
            }
        )

        lang = self.env.context.get("lang")
        if {"default_template_id", "default_model", "default_res_id"} <= ctx.keys():
            template = self.env["mail.template"].browse(ctx["default_template_id"])
            if template and template.lang:
                lang = template._render_lang([ctx["default_res_id"]])[
                    ctx["default_res_id"]
                ]

        self = self.with_context(lang=lang)
        if self.state in ["draft", "sent"]:
            ctx["model_description"] = _("Custom Request for Quotation")
        else:
            ctx["model_description"] = _("Purchase Order")

        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }
        
        
    def action_add_bids(self):
        self.ensure_one()
        if not self.vendor_ids:
            raise UserError("Please select vendors before requesting bids.")
        self.write({'state': 'bid_selection'})

    def action_view_bids(self):
        self.ensure_one()
        return {
            'name': 'Vendor Bids',
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.bid',
            'view_mode': 'tree,form',
            'domain': [('purchase_order_id', '=', self.id)],
            'context': {'default_purchase_order_id': self.id},
        }

    def action_select_bid(self):
        self.ensure_one()
        return {
            'name': 'Select Bid',
            'type': 'ir.actions.act_window',
            'res_model': 'select.bid.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id},
        }    
