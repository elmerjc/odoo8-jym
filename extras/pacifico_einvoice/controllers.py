# -*- coding: utf-8 -*-
from openerp import http

# class PacificoEinvoice(http.Controller):
#     @http.route('/pacifico_einvoice/pacifico_einvoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pacifico_einvoice/pacifico_einvoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pacifico_einvoice.listing', {
#             'root': '/pacifico_einvoice/pacifico_einvoice',
#             'objects': http.request.env['pacifico_einvoice.pacifico_einvoice'].search([]),
#         })

#     @http.route('/pacifico_einvoice/pacifico_einvoice/objects/<model("pacifico_einvoice.pacifico_einvoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pacifico_einvoice.object', {
#             'object': obj
#         })