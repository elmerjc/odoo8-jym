# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_invoice(models.Model):
    _inherit = "account.invoice"

    catalog_09_id = fields.Selection([
            ('01','Anulacion de la operacion'),
            ('02','Anulacion por error en el RUC'),
            ('03','Correccion por error en la descripcion'),
            ('04','Descuento global'),
            ('05','Descuento por item'),
            ('06','Devolucion total'),
            ('07','Devolucion por item'),
            ('08','Bonificacion'),
            ('09','Disminucion en el valor'),
        ], string='Motivo NC', index=True, 
        change_default=True, 
        track_visibility='always')
    catalog_10_id = fields.Selection([
            ('01','Interes por mora'),
            ('02','Aumento en el valor'),
            ('03','Penalidades'),
        ], string='Motivo ND', index=True, 
        change_default=True, 
        track_visibility='always')
    motivo_nc = fields.Char(string='Descripción', help="Descripción del motivo o sustento")
    invoice_nc_id = fields.Many2one('account.invoice', string='Factura relacionada', 
    	change_default=True,
    	track_visibility='always')
