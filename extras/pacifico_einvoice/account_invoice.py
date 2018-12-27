# -*- coding: utf-8 -*-

import base64
import os
import zipfile
import time
from num2words import num2words
from signxml import XMLSigner, XMLVerifier
from lxml import etree

from openerp import models, api, _
from openerp.tools import float_is_zero, float_round
from openerp.exceptions import Warning as UserError
import logging

logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'base.ubl']

    @api.multi
    def _ubl_add_extensions(self, parent_node, ns, version='2.0'):
        extensions_root = etree.SubElement(
            parent_node, ns['ext'] + 'UBLExtensions')
        ubl_extension = etree.SubElement(
            extensions_root, ns['ext'] + 'UBLExtension')
        extension_content = etree.SubElement(
            ubl_extension, ns['ext'] + 'ExtensionContent')
        self._ubl_add_additional_information(
           self.amount_total, False, 'AdditionalInformation', extension_content, ns, version=version)
        #self._ubl_add_extensions_signature(extensions_root, ns, version=version)

    @api.multi
    def _ubl_add_additional_information(self, amount_total, company, node_name, parent_node, ns, version='2.0'):
        additional_information_root = etree.SubElement(
            parent_node, ns['sac'] + node_name)

        AdditionalMonetaryTotal = etree.SubElement(
            additional_information_root, ns['sac'] + 'AdditionalMonetaryTotal')
        ID = etree.SubElement(
            AdditionalMonetaryTotal, ns['cbc'] + 'ID')
        ID.text = str(1002)
        PayableAmount = etree.SubElement(
            AdditionalMonetaryTotal, ns['cbc'] + 'PayableAmount', currencyID=self.currency_id.name)
        PayableAmount.text = str(amount_total)

        AdditionalProperty = etree.SubElement(
            additional_information_root, ns['sac'] + 'AdditionalProperty')
        ID = etree.SubElement(
            AdditionalProperty, ns['cbc'] + 'ID')
        ID.text = str(1000)
        Value = etree.SubElement(
            AdditionalProperty, ns['cbc'] + 'Value')
        Value.text = num2words(amount_total, lang='es').upper()

    @api.multi
    def _ubl_add_header(self, parent_node, ns, version='2.0'):
        ubl_version = etree.SubElement(
            parent_node, ns['cbc'] + 'UBLVersionID')
        ubl_version.text = version
        ubl_customizacion = etree.SubElement(
            parent_node, ns['cbc'] + 'CustomizationID')
        ubl_customizacion.text = '1.0'
        doc_id = etree.SubElement(parent_node, ns['cbc'] + 'ID')
        doc_id.text = self.number
        issue_date = etree.SubElement(parent_node, ns['cbc'] + 'IssueDate')
        issue_date.text = self.date_invoice
        type_code = etree.SubElement(
            parent_node, ns['cbc'] + 'InvoiceTypeCode')
        if self.type == 'out_invoice':
            type_code.text = '01'
        elif self.type == 'out_refund':
            type_code.text = '07'
        doc_currency = etree.SubElement(
            parent_node, ns['cbc'] + 'DocumentCurrencyCode')
        doc_currency.text = self.currency_id.name

    @api.multi
    def _ubl_add_attachments(self, parent_node, ns, version='2.0'):
        if (
                self.company_id.embed_pdf_in_ubl_xml_invoice and
                not self._context.get('no_embedded_pdf')):
            docu_reference = etree.SubElement(
                parent_node, ns['cac'] + 'AdditionalDocumentReference')
            docu_reference_id = etree.SubElement(
                docu_reference, ns['cbc'] + 'ID')
            docu_reference_id.text = 'Invoice-' + self.number + '.pdf'
            attach_node = etree.SubElement(
                docu_reference, ns['cac'] + 'Attachment')
            binary_node = etree.SubElement(
                attach_node, ns['cbc'] + 'EmbeddedDocumentBinaryObject',
                mimeCode="application/pdf")
            ctx = self._context.copy()
            ctx['no_embedded_ubl_xml'] = True
            pdf_inv = self.pool['report'].get_pdf(
                self._cr, self._uid, [self.id], 'account.report_invoice',
                context=ctx)
            binary_node.text = pdf_inv.encode('base64')

    @api.multi
    def _ubl_add_legal_monetary_total(self, parent_node, ns, version='2.0'):
        monetary_total = etree.SubElement(
            parent_node, ns['cac'] + 'LegalMonetaryTotal')
        cur_name = self.currency_id.name
        prec = self.env['decimal.precision'].precision_get('Account')
        """
        line_total = etree.SubElement(
            monetary_total, ns['cbc'] + 'LineExtensionAmount',
            currencyID=cur_name)
        line_total.text = '%0.*f' % (prec, self.amount_untaxed)
        tax_excl_total = etree.SubElement(
            monetary_total, ns['cbc'] + 'TaxExclusiveAmount',
            currencyID=cur_name)
        tax_excl_total.text = '%0.*f' % (prec, self.amount_untaxed)
        tax_incl_total = etree.SubElement(
            monetary_total, ns['cbc'] + 'TaxInclusiveAmount',
            currencyID=cur_name)
        tax_incl_total.text = '%0.*f' % (prec, self.amount_total)
        prepaid_amount = etree.SubElement(
            monetary_total, ns['cbc'] + 'PrepaidAmount',
            currencyID=cur_name)
        prepaid_value = self.amount_total - self.residual
        prepaid_amount.text = '%0.*f' % (prec, prepaid_value)
        """
        payable_amount = etree.SubElement(
            monetary_total, ns['cbc'] + 'PayableAmount',
            currencyID=cur_name)
        payable_amount.text = '%0.*f' % (prec, self.residual)

    @api.multi
    def _ubl_add_invoice_line(
            self, parent_node, iline, line_number, ns, version='2.0'):
        cur_name = self.currency_id.name
        line_root = etree.SubElement(
            parent_node, ns['cac'] + 'InvoiceLine')
        dpo = self.env['decimal.precision']
        qty_precision = dpo.precision_get('Product Unit of Measure')
        price_precision = dpo.precision_get('Product Price')
        account_precision = dpo.precision_get('Account')
        line_id = etree.SubElement(line_root, ns['cbc'] + 'ID')
        line_id.text = unicode(line_number)
        uom_unece_code = False
        # on v8, uos_id is not a required field on account.invoice.line
        if iline.uos_id and iline.uos_id.unece_code:
            uom_unece_code = iline.uos_id.unece_code
        if uom_unece_code:
            quantity = etree.SubElement(
                line_root, ns['cbc'] + 'InvoicedQuantity',
                unitCode='NIU')
        else:
            quantity = etree.SubElement(
                line_root, ns['cbc'] + 'InvoicedQuantity')
        qty = iline.quantity
        quantity.text = unicode(qty)
        line_amount = etree.SubElement(
            line_root, ns['cbc'] + 'LineExtensionAmount',
            currencyID=cur_name)
        line_amount.text = '%0.*f' % (account_precision, iline.price_subtotal)
        #PricingReference
        self._ubl_add_invoice_line_pricing_reference(
            iline, line_root, ns, version=version)
        self._ubl_add_invoice_line_tax_total(
            iline, line_root, ns, version=version)
        self._ubl_add_item(
            iline.name, iline.product_id, line_root, ns, type='sale',
            version=version)
        price_node = etree.SubElement(line_root, ns['cac'] + 'Price')
        price_amount = etree.SubElement(
            price_node, ns['cbc'] + 'PriceAmount', currencyID=cur_name)
        price_unit = 0.0
        # Use price_subtotal/qty to compute price_unit to be sure
        # to get a *tax_excluded* price unit
        if not float_is_zero(qty, precision_digits=qty_precision):
            price_unit = float_round(
                iline.price_subtotal / float(qty),
                precision_digits=price_precision)
        price_amount.text = unicode(price_unit)
        """
        if uom_unece_code:
            base_qty = etree.SubElement(
                price_node, ns['cbc'] + 'BaseQuantity',
                unitCode=uom_unece_code)
        else:
            base_qty = etree.SubElement(price_node, ns['cbc'] + 'BaseQuantity')
        base_qty.text = unicode(qty)
        """

    def _ubl_add_invoice_line_pricing_reference(
            self, iline, parent_node, ns, version='2.0'):
        cur_name = self.currency_id.name
        prec = self.env['decimal.precision'].precision_get('Account')
        pricing_reference_node = etree.SubElement(parent_node, ns['cac'] + 'PricingReference')
        
        condition_price_node = etree.SubElement(pricing_reference_node, ns['cac'] + 'AlternativeConditionPrice')
        price = iline.price_unit * (1 - (iline.discount or 0.0) / 100.0)
        
        price_amount_node = etree.SubElement(
            condition_price_node, ns['cbc'] + 'PriceAmount', currencyID=cur_name)
        price_amount_node.text = unicode(price)

        price_type_node = etree.SubElement(
            condition_price_node, ns['cbc'] + 'PriceTypeCode')
        price_type_node.text = '01'
        

    def _ubl_add_invoice_line_tax_total(
            self, iline, parent_node, ns, version='2.0'):
        cur_name = self.currency_id.name
        prec = self.env['decimal.precision'].precision_get('Account')
        tax_total_node = etree.SubElement(parent_node, ns['cac'] + 'TaxTotal')
        price = iline.price_unit * (1 - (iline.discount or 0.0) / 100.0)
        res_taxes = iline.invoice_line_tax_id.compute_all(
            price, iline.quantity, product=iline.product_id,
            partner=self.partner_id)
        tax_total = float_round(
            res_taxes['total_included'] - res_taxes['total'],
            precision_digits=prec)
        tax_amount_node = etree.SubElement(
            tax_total_node, ns['cbc'] + 'TaxAmount', currencyID=cur_name)
        tax_amount_node.text = unicode(tax_total)
        
        tax_subtotal_node = etree.SubElement(tax_total_node, ns['cac'] + 'TaxSubtotal')
        tax_amount_subtotal = etree.SubElement(
            tax_subtotal_node, ns['cbc'] + 'TaxAmount', currencyID=cur_name)
        tax_amount_subtotal.text = unicode(self.amount_tax) #modificar para impuestos

        tax_category_node = etree.SubElement(tax_subtotal_node, ns['cac'] + 'TaxCategory')
        tax_exemption = etree.SubElement(
            tax_category_node, ns['cbc'] + 'TaxExemptionReasonCode')
        tax_exemption.text = unicode(30) #verificar si es el codigo por exoneracion

        self._ubl_add_tax_scheme(tax_category_node, ns, version='2.0')

        """
        multitax
        for res_tax in res_taxes['taxes']:
            tax = self.env['account.tax'].browse(res_tax['id'])
            # we don't have the base amount in res_tax :-(
            self._ubl_add_tax_subtotal(
                False, res_tax['amount'], tax, cur_name, tax_total_node, ns,
                version=version)
        """
    @api.multi
    def get_delivery_partner(self):
        self.ensure_one()
        # NON, car nécessite un lien vers sale

    @api.multi
    def _ubl_add_tax_total(self, xml_root, ns, version='2.0'):
        self.ensure_one()
        cur_name = self.currency_id.name
        tax_total_node = etree.SubElement(xml_root, ns['cac'] + 'TaxTotal')
        tax_amount_node = etree.SubElement(
            tax_total_node, ns['cbc'] + 'TaxAmount', currencyID=cur_name)
        tax_amount_node.text = unicode(self.amount_tax)
        self._ubl_add_tax_subtotal(
                self.amount_untaxed, self.amount_tax, cur_name, tax_total_node, ns,
                version=version)
        """
        multitax
        for tline in self.tax_line:
            if not tline.base_code_id:
                raise UserError(_(
                    "Missing base code on tax line '%s'.") % tline.name)
            taxes = self.env['account.tax'].search([
                ('base_code_id', '=', tline.base_code_id.id)])
            if not taxes:
                raise UserError(_(
                    "The tax code '%s' is not linked to a tax.")
                    % tline.base_code_id.name)
            tax = taxes[0]
            self._ubl_add_tax_subtotal(
                tline.base, tline.amount, tax, cur_name, tax_total_node, ns,
                version=version)
        """
    
    @api.multi
    def generate_invoice_ubl_xml_etree(self, version='2.0'):
        nsmap, ns = self._ubl_get_nsmap_namespace('Invoice-2', version=version)
        xml_root = etree.Element('Invoice', nsmap=nsmap)
        self._ubl_add_extensions(xml_root, ns, version=version)
        self._ubl_add_header(xml_root, ns, version=version)
        #self._ubl_add_cac_signature(xml_root, ns, version=version)
        self._ubl_add_attachments(xml_root, ns, version=version)
        self._ubl_add_supplier_party(
            False, self.company_id, 'AccountingSupplierParty', xml_root, ns,
            version=version)
        self._ubl_add_customer_party(
            self.partner_id, False, 'AccountingCustomerParty', xml_root, ns,
            version=version)
        # delivery_partner = self.get_delivery_partner()
        # self._ubl_add_delivery(delivery_partner, xml_root, ns)
        # Put paymentmeans block even when invoice is paid ?
        """
        self._ubl_add_payment_means(
            self.partner_bank_id, self.payment_mode_id, self.date_due,
            xml_root, ns, version=version)
        if self.payment_term:
            self._ubl_add_payment_terms(
                self.payment_term, xml_root, ns, version=version)
        """
        self._ubl_add_tax_total(xml_root, ns, version=version)
        self._ubl_add_legal_monetary_total(xml_root, ns, version=version)

        line_number = 0
        for iline in self.invoice_line:
            line_number += 1
            self._ubl_add_invoice_line(
                xml_root, iline, line_number, ns, version=version)
        return xml_root

    @api.multi
    def generate_ubl_xml_string(self, version='2.0'):
        self.ensure_one()
        assert self.state in ('open', 'paid')
        assert self.type in ('out_invoice', 'out_refund')
        logger.debug('Starting to generate UBL XML Invoice file')
        lang = self.get_ubl_lang()
        # The aim of injecting lang in context
        # is to have the content of the XML in the partner's lang
        # but the problem is that the error messages will also be in
        # that lang. But the error messages should almost never
        # happen except the first days of use, so it's probably
        # not worth the additionnal code to handle the 2 langs
        xml_root = self.with_context(lang=lang).\
            generate_invoice_ubl_xml_etree(version=version)
        
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding="iso-8859-1",
            xml_declaration=True)
        self._ubl_check_xml_schema(xml_string, 'Invoice', version=version)
        logger.debug(
            'Invoice UBL XML file generated for account invoice ID %d '
            '(state %s)', self.id, self.state)
        logger.debug(xml_string)

         #firma
        #xml_string = self._ubl_add_signature(xml_string)
        
        return xml_string

    @api.multi
    def get_ubl_filename(self, version='2.0'):
        """This method is designed to be inherited"""
        #return 'UBL-Invoice-%s.xml' % version
        codigo_documento = '01'
        if self.type == 'out_refund':
            codigo_documento = '07'
        return '%s-%s-%s.xml' % (self.company_id.partner_id.x_ruc or company_id.partner_id.vat, codigo_documento, self.number)

    @api.multi
    def get_ubl_version(self):
        version = self._context.get('ubl_version') or '2.0'
        return version

    @api.multi
    def get_ubl_lang(self):
        return self.partner_id.lang or 'en_US'

    @api.multi
    def embed_ubl_xml_in_pdf(self, pdf_content):
        self.ensure_one()
        if (
                self.type in ('out_invoice', 'out_refund') and
                self.state in ('open', 'paid')):
            version = self.get_ubl_version()
            ubl_filename = self.get_ubl_filename(version=version)
            xml_string = self.generate_ubl_xml_string(version=version)
            pdf_content = self.embed_xml_in_pdf(
                xml_string, ubl_filename, pdf_content)
        return pdf_content

    @api.multi
    def attach_ubl_xml_file_button(self):
        self.ensure_one()
        assert self.type in ('out_invoice', 'out_refund')
        assert self.state in ('open', 'paid')
        version = self.get_ubl_version()
        xml_string = self.generate_ubl_xml_string(version=version)
        filename = self.get_ubl_filename(version=version)
        attach = self.env['ir.attachment'].create({
            'name': filename,
            'res_id': self.id,
            'res_model': unicode(self._model),
            'datas': xml_string.encode('base64'),
            'datas_fname': filename,
            # I have default_type = 'out_invoice' in context, so 'type'
            # would take 'out_invoice' value by default !
            'type': 'binary',
            })
        #actualizar el estado
        date_xml = time.strftime('%Y-%m-%d')
        self.write({'einvoice': 'xml', 'date_xml': date_xml})
        action = self.env['ir.actions.act_window'].for_xml_id(
            'base', 'action_attachment')
        action.update({
            'res_id': attach.id,
            'views': False,
            'view_mode': 'form,tree'
            })
        return action