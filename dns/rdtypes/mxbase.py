# Copyright (C) Dnspython Contributors, see LICENSE for text of ISC license

# Copyright (C) 2003-2007, 2009-2011 Nominum, Inc.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""MX-like base classes."""

import struct

import dns.exception
import dns.rdata
import dns.name


class MXBase(dns.rdata.Rdata):

    """Base class for rdata that is like an MX record."""

    __slots__ = ['preference', 'exchange']

    def __init__(self, rdclass, rdtype, preference, exchange):
        super().__init__(rdclass, rdtype)
        object.__setattr__(self, 'preference', preference)
        object.__setattr__(self, 'exchange', exchange)

    def to_text(self, origin=None, relativize=True, **kw):
        exchange = self.exchange.choose_relativity(origin, relativize)
        return '%d %s' % (self.preference, exchange)

    @classmethod
    def from_text(cls, rdclass, rdtype, tok, origin=None, relativize=True,
                  relativize_to=None):
        preference = tok.get_uint16()
        exchange = tok.get_name(origin, relativize, relativize_to)
        tok.get_eol()
        return cls(rdclass, rdtype, preference, exchange)

    def _to_wire(self, file, compress=None, origin=None, canonicalize=False):
        pref = struct.pack("!H", self.preference)
        file.write(pref)
        self.exchange.to_wire(file, compress, origin, canonicalize)

    @classmethod
    def from_wire(cls, rdclass, rdtype, wire, current, rdlen, origin=None):
        (preference, ) = struct.unpack('!H', wire[current: current + 2])
        current += 2
        rdlen -= 2
        (exchange, cused) = dns.name.from_wire(wire[: current + rdlen],
                                               current)
        if cused != rdlen:
            raise dns.exception.FormError
        if origin is not None:
            exchange = exchange.relativize(origin)
        return cls(rdclass, rdtype, preference, exchange)


class UncompressedMX(MXBase):

    """Base class for rdata that is like an MX record, but whose name
    is not compressed when converted to DNS wire format, and whose
    digestable form is not downcased."""

    def _to_wire(self, file, compress=None, origin=None, canonicalize=False):
        super()._to_wire(file, None, origin, False)


class UncompressedDowncasingMX(MXBase):

    """Base class for rdata that is like an MX record, but whose name
    is not compressed when convert to DNS wire format."""

    def _to_wire(self, file, compress=None, origin=None, canonicalize=False):
        super()._to_wire(file, None, origin, canonicalize)
