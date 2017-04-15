# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C (arc.pe).
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
    'name' : 'Comprobantes',
    'version' : '1.0',
    'category': 'Uncategorized',
    'author' : 'ARC',
    'website': "http://www.arc.pe",
    'summary' : 'Gestiona las comprobantes con los montos',
    'description' : 'Gestiona las comprobantes con los montos',
    'depends' : [
                'base',
                'sale',
                ],
    'data' : [
            'security/bolivia_security.xml',
            'security/ir.model.access.csv',
            'views/bolivia_layouts.xml',
            'views/report_comprobante.xml',
            'account_invoice_real_sequence.xml',
            'account_invoice_real_view.xml',
            'sale_view.xml',
            'account_invoice_real_report.xml',
            ],
    'installable' : True,
    'aplication' : True,
}
