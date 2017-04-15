# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-2016 S&C (<http://arc.pe>).
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
from openerp import api
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = 'sale.order'

    @api.one
    @api.depends('order_line')
    def _compute_quantity_total(self):
        self.quantity_total = sum(line.product_uom_qty for line in self.order_line)

    def _factura_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = False
            if sale.factura_ids:
                res[sale.id] = True
        return res

    def _factura_search(self, cursor, user, obj, name, args, context=None):
        if not len(args):
            return []
        clause = ''
        sale_clause = ''
        no_invoiced = False
        for arg in args:
            if (arg[1] == '=' and arg[2]) or (arg[1] == '!=' and not arg[2]):
                clause += 'AND inv.state = \'paid\''
            else:
                clause += 'AND inv.state != \'cancel\' AND sale.state != \'cancel\'  AND inv.state <> \'paid\'  AND rel.order_id = sale.id '
                sale_clause = ',  sale_order AS sale '
                no_invoiced = True

        cursor.execute('SELECT rel.order_id ' \
                'FROM sale_order_factura_rel AS rel, account_invoice_real AS inv '+ sale_clause + \
                'WHERE rel.invoice_id = inv.id ' + clause)
        res = cursor.fetchall()
        if no_invoiced:
            cursor.execute('SELECT sale.id ' \
                    'FROM sale_order AS sale ' \
                    'WHERE sale.id NOT IN ' \
                        '(SELECT rel.order_id ' \
                        'FROM sale_order_factura_rel AS rel) and sale.state != \'cancel\'')
            res.extend(cursor.fetchall())
        if not res:
            return [('id', '=', 0)]
        return [('id', 'in', [x[0] for x in res])]

    _columns = {
        'factura_ids': fields.many2many('account.invoice.real', 'sale_order_factura_rel', 'order_id', 'invoice_id', 'Facturas', readonly=True, copy=False),
        'factura_exists': fields.function(_factura_exists, string='Facturado',
            fnct_search=_factura_search, type='boolean', help="Indica si existe un comprobante asociado al pedido."),
        'quantity_total': fields.integer('Cantidad de pares', store=True, readonly=True, compute='_compute_quantity_total'),
        'partner_nit': fields.char(related='partner_id.x_ruc', string='NIT', store=True, readonly=True),
    }

    def _prepare_factura(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}
        domain = [
            ('name', '=', 'BOL'),
        ]
        currency_id = self.pool.get('res.currency').search(cr, uid, domain, limit=1)

        invoice_vals = {
            'name': order.name or '',
            'origin': order.name,
            'partner_id': order.partner_invoice_id.id,
            'invoice_line': [(6, 0, lines)],
            'currency_id': currency_id[0],
            'date_invoice': order.date_order,
            'user_id': order.user_id and order.user_id.id or False,
            'amount_untaxed' : order.amount_untaxed,
            'amount_tax' : order.amount_tax,
            'amount_total' : order.amount_total,
        }

        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

    def _make_factura(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice.real')
        if context is None:
            context = {}

        inv = self._prepare_factura(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        self.write(cr, uid, [order.id], {'state': 'progress'}, context=context)
        return inv_id

    def action_view_factura(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'bolivia_factura', 'listar_invoice_real')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            inv_ids += [invoice.id for invoice in so.factura_ids]
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'bolivia_factura', 'invoice_real_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result

    def action_factura_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice.real')
        obj_sale_order_line = self.pool.get('sale.order.line')

        if date_invoice:
            context = dict(context or {}, date_invoice=date_invoice)

        for o in self.browse(cr, uid, ids, context=context):
            lines = []
            for line in o.order_line:
                lines.append(line.id)
            created_lines = obj_sale_order_line.factura_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.partner_id.id, []).append((o, created_lines))

        for val in invoices.values():
            for order, il in val:
                res = self._make_factura(cr, uid, order, il, context=context)
                invoice_ids.append(res)
                cr.execute('insert into sale_order_factura_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
                self.invalidate_cache(cr, uid, ['factura_ids'], [order.id], context=context)
        self.action_view_factura(cr, uid, ids)
        return res

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'factura_lines': fields.many2many('account.invoice.line.real', 'sale_order_line_factura_rel', 'order_line_id', 'invoice_id', 'Items de la factura', readonly=True, copy=False),
    }

    def _prepare_order_line_factura_line(self, cr, uid, line, account_id=False, context=None):
        res = {}
        uosqty = self._get_line_qty(cr, uid, line, context=context)
        uos_id = self._get_line_uom(cr, uid, line, context=context)
        pu = 0.0
        if uosqty:
            pu = round(line.price_unit * line.product_uom_qty / uosqty,
                    self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
        fpos = line.order_id.fiscal_position or False

        res = {
            'name': line.name,
            'sequence': line.sequence,
            'origin': line.order_id.name,
            'price_unit': pu,
            'price_subtotal' : line.price_subtotal,
            'quantity': uosqty,
            'product_id': line.product_id.id or False,
        }

        return res

    def factura_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        create_ids = []
        sales = set()
        for line in self.browse(cr, uid, ids, context=context):
            vals = self._prepare_order_line_factura_line(cr, uid, line, False, context)
            if vals:
                inv_id = self.pool.get('account.invoice.line.real').create(cr, uid, vals, context=context)
                self.write(cr, uid, [line.id], {'factura_lines': [(4, inv_id)]}, context=context)
                sales.add(line.order_id.id)
                create_ids.append(inv_id)
        return create_ids