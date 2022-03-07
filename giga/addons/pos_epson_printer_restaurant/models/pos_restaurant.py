# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models

class RestaurantPrinter(models.Model):

    _inherit = 'restaurant.printer'

    printer_type = fields.Selection(selection_add=[('epson_epos', 'Use an Epson printer')])
    epson_printer_ip = fields.Char(string='Epson Receipt Printer IP Address', help="Local IP address of an Epson receipt printer.")
