# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 S&C ().
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
    'name' : 'JYM Soluciones',
    'version' : '1.0',
    'category': 'Uncategorized',
    'author' : 'ARC',
    'website': "http://www.arc.pe",
    'summary' : 'Creación de vistas y modelos para JYM',
    'description' : 'Creación de vistas y modelos para JYM',
    'depends' : [
                'base',
                'report',
                'account',
                ],
    'data' : [
            'account_invoice_view.xml',
            'views/boleta_layouts.xml',
            'views/boleta_report.xml',
            'views/factura_layouts.xml',
            'views/factura_report.xml',
            'views/proforma_layouts.xml',
            'views/proforma_report.xml',
            'views/proforma2_report.xml',
            ],
    'installable' : True,
    'aplication' : True,
}
