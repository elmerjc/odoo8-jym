# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, api

class res_partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_url_parameters_partner_vals(self, partner):
        info = []
        if partner.street2:
            info.append(partner.street2)
        return '+'.join(info).replace(' ', '+')

    @api.multi
    def open_map(self):
        base_url = "http://maps.google.com/maps?oi=map&q="
        for partner in self:
            url = base_url + self._get_url_parameters_partner_vals(partner)
            return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                    }
