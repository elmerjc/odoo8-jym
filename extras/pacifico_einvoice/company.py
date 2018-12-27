# -*- coding: utf-8 -*-

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    embed_pdf_in_ubl_xml_invoice = fields.Boolean(
        string='Embed PDF in UBL XML Invoice',
        help="If active, the standalone UBL Invoice XML file will include the "
        "PDF of the invoice in base64 under the node "
        "'AdditionalDocumentReference'. For example, to be compliant with the "
        "e-fff standard used in Belgium, you should activate this option.")
