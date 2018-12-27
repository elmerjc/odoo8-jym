# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C (takanags.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name' : 'Facturas de proveedores',
    'version' : '1.0',
    'category': 'Uncategorized',
    'author' : 'TakanaGS',
    'website': "http://www.takanags.com",
    'summary' : 'Gestiona Facturas de proveedores',
    'description' : 'Gestiona Facturas de proveedores',
    'depends' : [
                'base',
                'account',
                'report',
                ],
    'data' : [
            'security/takana_invoice.xml',
            'security/ir.model.access.csv',
            'takana_invoice_sequence.xml',
            'takana_invoice_view.xml',
            'takana_payment_view.xml',
            'currency_view.xml',
            'wizard/wizard_add_dues_view.xml',
            'wizard/wizard_report_invoice_view.xml',
            'wizard/wizard_report_payment_view.xml',
            'takana_payment_report.xml',
            'report/report_payment_view.xml',
            'views/takana_layouts.xml',
            'views/report_invoice.xml',
            'views/report_payment.xml',
            ],
    'installable' : True,
    'aplication' : True,
}
