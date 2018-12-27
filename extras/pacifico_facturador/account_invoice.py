# -*- coding: utf-8 -*-
import base64
import os
import zipfile

from openerp import models, api, _
from openerp.osv import fields, osv
from openerp.tools import float_is_zero, float_round
from openerp.exceptions import Warning as UserError
import logging
import time

logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_ubl_version(self):
        version = self._context.get('ubl_version') or '2.0'
        return version

    @api.multi
    def get_ubl_filename(self, version='2.0'):
        codigo_documento = '01'
        if self.type == 'out_refund':
            codigo_documento = '07'
        return '%s-%s-%s.xml' % (self.company_id.partner_id.x_ruc or company_id.partner_id.vat, codigo_documento, self.number)

    @api.multi
    def create_file_cab(self):
        self.ensure_one()
        version = self.get_ubl_version()
        filename_xml = self.get_ubl_filename(version=version)
        filename = filename_xml.replace(".xml", ".cab")
        cur_name = self.currency_id.name
        price_precision = self.env['decimal.precision'].precision_get('Account')

        if not self.partner_id.catalog_06_id.code:
            raise osv.except_osv(_('Tipo de documento no definido!'), _('El tipo de documento del cliente,\n no esta definido.'))

        path = "/opt/tmp/"
        file = open(path + filename,"w+")

        numero_identidad = self.partner_id.x_ruc or self.partner_id.vat

        if self.partner_id.catalog_06_id.code == '0' or self.partner_id.catalog_06_id.code == 0:
            tipo_operacion = "03"
            numero_identidad = "-"
        else:
            tipo_operacion = "01"
            numero_identidad = self.partner_id.x_ruc or self.partner_id.vat

        separador = "|"
        cab_text = tipo_operacion
        cab_text += separador
        cab_text += self.date_invoice
        cab_text += separador
        cab_text += "1"
        cab_text += separador
        cab_text += self.partner_id.catalog_06_id.code
        cab_text += separador
        cab_text += numero_identidad
        cab_text += separador
        cab_text += self.partner_id.name
        cab_text += separador
        cab_text += cur_name
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        #total con el numero decimales
        total = round(self.amount_total, price_precision)
        total_str = "%.2f" % total
        cab_text += total_str
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += "0.00"
        cab_text += separador
        cab_text += total_str
        cab_text += separador

        file.write(cab_text)

        #file_data = file.read()

        attach = self.env['ir.attachment'].create({
            'name': filename,
            'res_id': self.id,
            'res_model': unicode(self._model),
            'datas': cab_text.encode('utf8').encode('base64'),
            'datas_fname': filename,
            'type': 'binary',
        })

        file.close()

        return True

    @api.multi
    def create_file_det(self):
        self.ensure_one()
        version = self.get_ubl_version()
        filename_xml = self.get_ubl_filename(version=version)
        filename = filename_xml.replace(".xml", ".det")
        cur_name = self.currency_id.name

        path = "/opt/tmp/"
        file = open(path + filename,"w+")
        file.close()
        file = open(path + filename,"a+")

        price_precision = self.env['decimal.precision'].precision_get('Account')
        line_number = 0
        line_text = ""
        separador = "|"

        if self.partner_id.catalog_06_id.code == '0' or self.partner_id.catalog_06_id.code == 0:
            afectacion_igv = "40"
        else:
            afectacion_igv = "30"

        for line in self.invoice_line:
            product_name = "%s %s/%s" % (line.product_id.name, line.product_id.x_recibo, line.product_id.x_item)
            line_number += 1
            line_text += "PR"
            line_text += separador
            qty = round(line.quantity, 0)
            line_text += unicode(qty)
            line_text += separador
            line_text += line.product_id.default_code or line.product_codigo
            line_text += separador
            line_text += ""
            line_text += separador
            line_text += product_name
            line_text += separador
            price = round(line.price_unit, price_precision)
            price_str = "%.2f" % price
            line_text += price_str
            line_text += separador
            line_text += "0.00"
            line_text += separador
            line_text += "0.00"
            line_text += separador
            line_text += afectacion_igv
            line_text += separador
            line_text += "0.00"
            line_text += separador
            line_text += ""
            line_text += separador
            subtotal = round(line.price_subtotal, price_precision)
            subtotal_str = "%.2f" % subtotal
            line_text += subtotal_str
            line_text += separador
            line_text += subtotal_str
            line_text += separador
            line_text += "\r"
            file.write(line_text)

        attach = self.env['ir.attachment'].create({
            'name': filename,
            'res_id': self.id,
            'res_model': unicode(self._model),
            'datas': line_text.encode('utf8').encode('base64'),
            'datas_fname': filename,
            'type': 'binary',
        })

        file.close()

        return True

    @api.multi
    def create_file_not(self):
        self.ensure_one()
        version = self.get_ubl_version()
        filename_xml = self.get_ubl_filename(version=version)
        filename = filename_xml.replace(".xml", ".not")
        cur_name = self.currency_id.name

        path = "/opt/tmp/"
        file = open(path + filename,"w+")

        #Tipo de documento de referencia
        if self.invoice_nc_id.type == 'out_invoice':
            tipo_documento = "01"

        separador = "|"
        not_text = ""
        
        not_text += self.date_invoice
        not_text += separador
        not_text += self.catalog_09_id
        not_text += separador
        not_text += self.motivo_nc
        not_text += separador
        not_text += tipo_documento
        not_text += separador
        not_text += self.invoice_nc_id.number
        not_text += separador
        not_text += self.partner_id.catalog_06_id.code
        not_text += separador
        not_text += self.partner_id.x_ruc or self.partner_id.vat
        not_text += separador
        not_text += self.partner_id.name
        not_text += separador
        not_text += cur_name
        not_text += separador
        not_text += ""
        not_text += separador
        not_text += "0.00"
        not_text += separador
        not_text += unicode(self.amount_total)
        not_text += separador
        not_text += "0.00"
        not_text += separador
        not_text += "0.00"
        not_text += separador
        not_text += "0.00"
        not_text += separador
        not_text += "0.00"
        not_text += separador
        not_text += unicode(self.amount_total)
        not_text += separador

        file.write(not_text)

        #file_data = file.read()

        attach = self.env['ir.attachment'].create({
            'name': filename,
            'res_id': self.id,
            'res_model': unicode(self._model),
            'datas': not_text.encode('iso-8859-1').encode('base64'),
            'datas_fname': filename,
            'type': 'binary',
        })

        file.close()

        return True

    @api.multi
    def create_file_txt(self):
        if self.type == 'out_refund':
            self.create_file_not()
            self.create_file_det()
        if self.type == 'out_invoice':
            self.create_file_cab()
            self.create_file_det()
        
        return True