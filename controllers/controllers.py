# -*- coding: utf-8 -*-
# from odoo import http


# class Credito(http.Controller):
#     @http.route('/credito/credito/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/credito/credito/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('credito.listing', {
#             'root': '/credito/credito',
#             'objects': http.request.env['credito.credito'].search([]),
#         })

#     @http.route('/credito/credito/objects/<model("credito.credito"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('credito.object', {
#             'object': obj
#         })
