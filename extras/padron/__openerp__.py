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
    'name' : 'Padron de Sindicato',
    'version' : '1.0',
    'category': 'Uncategorized',
    'author' : 'ARC',
    'website': "http://www.arc.pe",
    'summary' : 'Modulo para el control de miembros de un sindicato',
    'description' : 'Modulo para el control de miembros de un sindicato',
    'depends' : [
                'base',
                'report',
                ],
    'data' : [
            'padron_view.xml',
            'padron_report.xml',
            'views/padron_layouts.xml',
            'views/report_trabajadores.xml',
            'report/padron_report_view.xml',
            ],
    'installable' : True,
    'aplication' : True,
}
