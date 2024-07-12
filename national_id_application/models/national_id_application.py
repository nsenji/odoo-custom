
from odoo import models, fields

class NationalIDApplication(models.Model):
    _name = 'national.id.application'
    _description = 'National Id Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Applicant Name', required=True)
    email = fields.Char(string="Email", required= True)
    dob = fields.Date(string='Date of Birth', required=True)
    place_of_birth = fields.Char(string='Place of Birth', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', required=True)
    address = fields.Text(string='Address', required=True)
    photo = fields.Binary(string='Applicant Photo', attachment=True)
    lc_reference_letter = fields.Binary(string='LC Reference Letter', attachment=True)
    state = fields.Selection([('draft', 'Draft'), ('first_approval', 'First Approval'), ('second_approval', 'Second Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], string='State', default='first_approval', tracking=True)

    def action_stage1(self):
        self.state = 'stage1'
        # self.message_post(body='Moved to Stage 1')

    def action_stage2(self):
        self.state = 'stage2'
        # self.message_post(body='Moved to Stage 2')

    def action_approve(self):
        self.state = 'approved'
        # self.message_post(body='Application Approved')
