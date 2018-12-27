# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C (<http://aroc.pe>).
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
    'name' : 'JYM Soluciones Report',
    'version' : '1.0',
    'category': 'Uncategorized',
    'author' : 'AROC',
    'website': "http://www.aroc.pe",
    'summary' : 'Modulo de Reportes para JYM Soluciones',
    'description' : 'Modulo de Reportes para JYM Soluciones',
    'depends' : [
                'base',
                'product',
                'sale',
                'report',
                ],
    'data' : [
            'security/jym_security.xml',
            'security/ir.model.access.csv',
            'report/jym_report_view.xml',
            'product_template_view.xml',
            'sale_order_line_view.xml',
            'account_voucher_report.xml',
            'views/voucher_print_layout.xml',
            'views/report_voucher_print.xml',
            ],
    'installable' : True,
    'aplication' : True,
}
