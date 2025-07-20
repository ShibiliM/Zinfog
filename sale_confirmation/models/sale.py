from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    automated_workflow= fields.Boolean(string="Automated Workflow", default=False)
    manager_reference = fields.Char('Manager Reference')
    can_edit_manager_reference = fields.Boolean(compute='_compute_can_edit_manager_reference')

    @api.depends('user_id')  # Optional trigger
    def _compute_can_edit_manager_reference(self):
        for order in self:
            user = self.env.user
            order.can_edit_manager_reference = user.has_group('sale_confirmation.group_sale_admin')

    def _automated_delivery_workflow(self, order):
        # Cancel existing draft/confirmed pickings
        for picking in order.picking_ids.filtered(lambda p: p.state in ['draft', 'confirmed']):
            picking.action_cancel()
        if not order.procurement_group_id:
            group = self.env['procurement.group'].create({
                'name': order.name,
                'partner_id': order.partner_id.id,
            })
            order.procurement_group_id = group
        else:
            group = order.procurement_group_id

        # Group order lines by product (same product_id)
        product_lines_map = defaultdict(list)
        for line in order.order_line:
            if line.product_id.type != 'product':
                continue
            product_lines_map[line.product_id.id].append(line)


        # Create one picking per product (grouped by product ID)
        for product_id, lines in product_lines_map.items():

            picking = self.env['stock.picking'].create({
                'partner_id': order.partner_id.id,
                'picking_type_id': order.warehouse_id.out_type_id.id,
                'origin': order.name,
                'location_id': order.warehouse_id.lot_stock_id.id,
                'location_dest_id': order.partner_id.property_stock_customer.id,
                'company_id': order.company_id.id,
                'sale_id': order.id,
                'group_id': group.id,
            })

            for line in lines:
                self.env['stock.move'].create({
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': order.warehouse_id.lot_stock_id.id,
                    'location_dest_id': order.partner_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'company_id': order.company_id.id,
                    'origin': order.name,
                    'description_picking': line.product_id.name,
                    'sale_line_id': line.id,
                    'group_id': group.id,
                })

            # Confirm and validate picking
            picking.action_confirm()
            if picking.state in ['confirmed', 'waiting']:
                picking.action_assign()
            for move_line in picking.move_ids_without_package:
                move_line.quantity_done = move_line.product_uom_qty
            picking.button_validate()


    def action_confirm(self):
        config_param = self.env['ir.config_parameter'].sudo()
        approval_amount = float(config_param.get_param('sale.sale_order_approval_amount', default=5000.0))

        confirmed_orders = self.env['sale.order']

        for order in self:
            if self.env.user.has_group('sale_confirmation.group_sale_admin'):
                if order.automated_workflow:
                    self._automated_delivery_workflow(order)
                    confirmed_orders += order
                else:
                    super(SaleOrder, order).action_confirm()
            elif order.amount_total >= approval_amount:
                raise UserError("This order can only be confirmed by sales admin!")
            else:
                if order.automated_workflow:
                    self._automated_delivery_workflow(order)
                    confirmed_orders += order
                else:
                    super(SaleOrder, order).action_confirm()

        # Confirm orders that were auto processed
        super(SaleOrder, confirmed_orders).action_confirm()

        confirmed_orders._force_lines_to_invoice_policy_order()

        # Create invoices and register payment
        for order in confirmed_orders:
            if any(line.qty_to_invoice > 0 for line in order.order_line):
                invoices = order._create_invoices()
                for invoice in invoices:
                    invoice._portal_ensure_token()
                    invoice.action_post()

                    wizard_ctx = {
                        'active_model': 'account.move',
                        'active_ids': invoice.ids,
                    }

                    payment_register = self.env['account.payment.register'].with_context(**wizard_ctx).new({
                        'amount': invoice.amount_residual,
                        'payment_date': fields.Date.today(),
                    })

                    journal = self.env['account.journal'].browse(payment_register.available_journal_ids[:1].ids)
                    if not journal:
                        raise UserError("No available journal found to register payment.")

                    method = journal.inbound_payment_method_line_ids[:1]
                    if not method:
                        raise UserError("Selected journal has no inbound payment method.")

                    self.env['account.payment.register'].with_context(**wizard_ctx).create({
                        'journal_id': journal.id,
                        'payment_method_line_id': method.id,
                        'amount': invoice.amount_residual,
                        'payment_date': fields.Date.today(),
                    })._create_payments()
                order.invoice_status = 'invoiced'

        return confirmed_orders







