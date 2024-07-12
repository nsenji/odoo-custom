from odoo import models, fields


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
        string="State",
        default="pending",
        index=True,
        copy=False,
        tracking=True,
    )

    def action_first_approval(self):
        self.write({"state": "stage_1"})
        # self.message_post(body='Moved to Stage 1')

    def action_second_approval(self):
        self.write({"state": "approved"})

    # self.message_post(body='Moved to Stage 2')

    # def action_done(self):
    #     self.write({"state": "approved"})
    #     # self.message_post(body='Application Approved')

    def reject_application(self):
        self.write({"state": "rejected"})
