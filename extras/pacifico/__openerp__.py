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
    'name' : 'Pacifico',
    'version': '8.0.1.0.0',
    'category': 'Pacifico',
    'author' : 'ARC',
    'website': "http://www.arc.pe",
    'summary' : 'Modulo para Distribuidor del Pacifico',
    'description' : 'Modulo para Distribuidor del Pacifico',
    'depends' : [
                'sale',
                'account',
                ],
    'data' : [
            'security/pacifico_security.xml',
            'security/ir.model.access.csv',
            'views/account_invoice.xml',
            'views/sale_order.xml',
            'wizard/wizard_report_sale_invoice_view.xml',
            ],
    'active': False,
    'installable' : True,
}
