"""Exercise response boundaries using the real Zope HTTPResponse."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ZPublisher.HTTPResponse import HTTPResponse
from plone.transformchain.zpublisher import applyTransformOnSuccess


class ResponseBoundaryTests(unittest.TestCase):
    def transform(self, chunks, content_type):
        response = HTTPResponse()
        response.setHeader('Content-Type', content_type)
        response.setStatus(201)
        event = SimpleNamespace(request=SimpleNamespace(response=response))
        with patch('plone.transformchain.zpublisher.applyTransform',
                   return_value=iter(chunks)):
            applyTransformOnSuccess(event)
        self.assertEqual(response.getStatus(), 201)
        self.assertEqual(response.getHeader('content-length'),
                         str(len(response.getBody())))
        return response.getBody()

    def test_non_utf8_bytes(self):
        self.assertEqual(self.transform([b'Gr\xfc', b'n'],
                         'text/plain; charset=iso-8859-1'), b'Gr\xfcn')

    def test_binary_chunks_are_not_decoded(self):
        self.assertEqual(self.transform([b'\xff\x00', b'\x80'],
                         'application/octet-stream'), b'\xff\x00\x80')

    def test_mixed_text_and_bytes_use_response_charset(self):
        self.assertEqual(self.transform(['Grün', b'!'],
                         'text/plain; charset=iso-8859-1'), b'Gr\xfcn!')

    def test_unicode_chunks(self):
        self.assertEqual(self.transform(['Grün', '日本'],
                         'text/plain; charset=utf-8'), 'Grün日本'.encode())
