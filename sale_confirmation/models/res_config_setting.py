from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_approval = fields.Boolean(string="Require Approval for Sale Orders", config_parameter="sale.sale_order_approval")
    sale_order_approval_amount = fields.Float(string="Sale order limit", config_parameter="sale.sale_order_approval_amount", default=5000.0)