from odoo import http
from odoo.http import request
import base64

class NationalIDController(http.Controller):

    @http.route('/', type='http', auth='public', website=True)
    def national_id_form(self, **kw):
        return request.render("national_id_application.national_id_form_template", {})

    @http.route('/submit', type='http', auth='public', website=True, methods=['POST'])
    def submit_national_id_application(self, **post):
      
        vals = {
            'name': post.get('name'),
            'email': post.get('email'),
            'dob': post.get('dob'),
            'place_of_birth': post.get('place_of_birth'),
            'gender': post.get('gender'),
            'address': post.get('address'),
        }

       
        application = request.env['national.id.application'].sudo().create(vals)

    
        if 'photo' in request.httprequest.files:
            photo = request.httprequest.files['photo']
            application.sudo().write({
                'photo': base64.b64encode(photo.read()),
            })

        if 'lc_reference_letter' in request.httprequest.files:
            lc_letter = request.httprequest.files['lc_reference_letter']
            application.sudo().write({
                'lc_reference_letter': base64.b64encode(lc_letter.read()),
            })

        return request.render("national_id_application.application_submitted", {
            'application': application,
        })