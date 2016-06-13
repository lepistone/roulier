# -*- coding: utf-8 -*-
"""Implementation for trs."""
from roulier.transport import Transport
from jinja2 import Environment, PackageLoader
from collections import OrderedDict
import unicodecsv as csv
from io import BytesIO


class TrsTransport(Transport):
    """Generate ZPL offline and csv for EDI."""

    STATUS_SUCCESS = "Success"

    def send(self, body):
        """Call this function.

        Args:
            body: an object with a lot usefull values
        Return:
            {
                status: STATUS_SUCCES or STATUS_ERROR, (string)
                message: more info about status of result (None)
                response: (None)
                payload: usefull payload (if success) (body as string)

            }
        """
        payload = {
            'zpl': self.generate_zpl(body),
            'meta': self.map_delivery_line(body),
        }
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": payload,
        }

    def generate_zpl(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/trs/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("trs_generateLabel.zpl")
        return template.render(
            auth=body['auth'],
            service=body['service'],
            outputFormat=body['output_format'],
            parcel=body['parcel'],
            sender_address=body['sender_address'],
            receiver_address=body['receiver_address'])

    def map_delivery_line(self, body):
        data = OrderedDict([
            (u'client', body['sender_address']['companyName']),
            (u'siret', None),
            (u'refCommande', body['service']['shippingReference']),
            (u'dateEnlevement', body['service']['shippingDate']),
            (u'cr', None),
            (u'va', None),
            (u'nom', body['receiver_address']['name']),
            (u'adr1', body['receiver_address']['street1']),
            (u'adr2', body['receiver_address']['street2']),
            (u'cp', body['receiver_address']['zipCode']),
            (u'ville', body['receiver_address']['city']),
            (u'telephone', body['receiver_address']['phoneNumber']),
            (u'mobile', body['receiver_address']['phoneNumber']),
            (u'email', body['receiver_address']['email']),
            (u'refDest', None),
            (u'commentLiv', None),
            (u'nbConducteurs', None),
            (u'Poids', body['parcel']['weight']),
            (u'nbColis', None),
            (u'qtéFacturée1', None),
            (u'qtéFacturée2', None),
            (u'qtéFacturée3', None),
            (u'qtéFacturée4', None),
            (u'qtéFacturée5', None),
            (u'qtéFacturée6', None),
            (u'qtéFacturée7', None),
            (u'qtéFacturée8', None),
            (u'qtéFacturée9', None),
            (u'qtéFacturée10', None),
            (u'article1', None),
            (u'article2', None),
            (u'article3', None),
            (u'article4', None),
            (u'article5', None),
            (u'article6', None),
            (u'article7', None),
            (u'article8', None),
            (u'article9', None),
            (u'article10', None),
            (u'regroupement', None),
            (u'refComfour', None),
            (u'codeBarre', body['parcel']['barcode']),
            (u'descColis', None),
            (u'porteur', None),
            (u'jourLivraison', None),
        ])
        return data

    def generate_deposit_slip(self, rows):
        output = BytesIO()

        # l'ordre est important
        headers = rows[0].keys()

        # l'ordre est fixé par headers
        writer = csv.DictWriter(output, headers, encoding='utf-8')
        writer.writeheader()
        writer.writerows(rows)
        return output
