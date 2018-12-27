# -*- coding: utf-8 -*-

import time
from openerp.osv import osv
from openerp import models, fields, api

class account_invoice(models.Model):
    _inherit = "account.invoice"

    invoice_cba = fields.Boolean(string='Comunicacion de baja')
    date_cba = fields.Date(string='Fecha de envio')
    motivo_cba = fields.Char(string='Motivo de baja')

    @api.multi
    def create_file_cba(self):
        self.ensure_one()

        if not self.motivo_cba:
            raise osv.except_osv('No ingreso el motivo de baja', 'Debe ingresar el motivo de la baja,\n para ser enviado a la SUNAT.')

        ruc = self.company_id.partner_id.x_ruc or company_id.partner_id.vat
        date_cba = self.date_cba or time.strftime('%Y-%m-%d')
        date_cba_name = time.strftime('%Y%m%d')
        invoice_cba = self.search([('invoice_cba','=',True),('date_cba','=',date_cba)], count=True)
        if not invoice_cba:
            correlativo = 1
        else:
            correlativo = invoice_cba

        filename = (ruc + "-RA-" + date_cba_name + "-" + ("%03d" % correlativo) + ".cba")
        cur_name = self.currency_id.name

        path = "/opt/tmp/"
        file = open(path + filename,"w+")

        #Tipo de documento de referencia
        if self.type == 'out_invoice':
            tipo_documento = "01"
        if self.type == 'out_refund':
            tipo_documento = "07"

        cab_text = ""
        separador = "|"

        cab_text += self.date_invoice
        cab_text += separador
        cab_text += date_cba
        cab_text += separador
        cab_text += tipo_documento
        cab_text += separador
        cab_text += self.internal_number or self.number
        cab_text += separador
        cab_text += self.motivo_cba
        cab_text += separador
        
        file.write(cab_text)

        attach = self.env['ir.attachment'].create({
            'name': filename,
            'res_id': self.id,
            'res_model': unicode(self._model),
            'datas': cab_text.encode('iso-8859-1').encode('base64'),
            'datas_fname': filename,
            'type': 'binary',
        })

        file.close()

        return True