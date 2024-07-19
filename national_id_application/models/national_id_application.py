from odoo import models, fields, _


class NationalIDApplication(models.Model):
    _name = "national.id.application"
    _description = "National Id Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Applicant Name", required=True)
    email = fields.Char(string="Email", required=True)
    dob = fields.Date(string="Date of Birth", required=True)
    place_of_birth = fields.Char(string="Place of Birth", required=True)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")], string="Gender", required=True
    )
    address = fields.Text(string="Address", required=True)
    photo = fields.Binary(string="Applicant Photo", attachment=True)
    lc_reference_letter = fields.Binary(string="LC Reference Letter", attachment=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("stage_1", "Stage 1"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="pending",
        index=True,
        copy=False,
        tracking=True,
    )

    def action_first_approval(self):
        self.write({"state": "stage_1"})

    def action_second_approval(self):
        self.write({"state": "approved"})

    def reject_application(self):
        self.write({"state": "rejected"})

    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env["ir.model.data"]

        try:
            if self.env.context.get("send_approval", False):
                template_id = ir_model_data._xmlid_lookup(
                    "national_id_application.email_template_national_id_approval"
                )[1]
            else:
                template_id = ir_model_data._xmlid_lookup(
                    "national_id_application.email_template_national_id_rejection"
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
                "default_model": "national.id.application",
                "default_res_ids": self.ids,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
                "force_email": True,
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
