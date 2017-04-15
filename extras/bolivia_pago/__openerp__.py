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
    'name' : 'Pagos comprobante',
    'version' : '1.0',
    'category': 'Uncategorized',
    'author' : 'ARC',
    'website': "http://www.arc.pe",
    'summary' : 'Gestiona los pagos de los comprobantes',
    'description' : 'Gestiona los pagos de los comprobantes',
    'depends' : [
                'base',
                'bolivia_factura',
                'sale',
                ],
    'data' : [
            'security/bolivia_security.xml',
            'security/ir.model.access.csv',
            'bolivia_pago_view.xml',
            'bolivia_pago_report.xml',
            'partner_view.xml',
            'sale_view.xml',
            'wizard/report_balance_pagos_wizard_view.xml',
            'views/bolivia_pago_layouts.xml',
            'views/report_balance_pagos.xml',
            ],
    'installable' : True,
    'aplication' : True,
}
