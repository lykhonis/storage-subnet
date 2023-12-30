import base58
import multibase
import multihash as mh
import multicodec
from morphys import ensure_bytes, ensure_unicode


class BaseCID(object):
    __hash__ = object.__hash__

    def __init__(self, version, codec, multihash):
        """
        Creates a new CID object. This class should not be used directly, use :py:class:`cid.cid.CIDv0` or
        :py:class:`cid.cid.CIDv1` instead.


        :param int version: CID version (0 or 1)
        :param str codec: codec to be used for encoding the hash
        :param str multihash: the multihash
        """
        self._version = version
        self._codec = codec
        self._multihash = ensure_bytes(multihash)

    @property
    def version(self):
        """CID version"""
        return self._version

    @property
    def codec(self):
        """CID codec"""
        return self._codec

    @property
    def multihash(self):
        """CID multihash"""
        return self._multihash

    @property
    def buffer(self):
        raise NotImplementedError

    def encode(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        def truncate(s, length):
            return s[:length] + b".." if len(s) > length else s

        truncate_length = 20
        return (
            "{class_}(version={version}, codec={codec}, multihash={multihash})".format(
                class_=self.__class__.__name__,
                version=self._version,
                codec=self._codec,
                multihash=truncate(self._multihash, truncate_length),
            )
        )

    def __str__(self):
        return ensure_unicode(self.encode())

    def __eq__(self, other):
        return (
            (self.version == other.version)
            and (self.codec == other.codec)
            and (self.multihash == other.multihash)
        )


class CIDv1(BaseCID):
    """CID version 1 object"""

    def __init__(self, codec, multihash):
        super(CIDv1, self).__init__(1, codec, multihash)

    @property
    def buffer(self):
        """
        The raw representation of the CID

        :return: raw representation of the CID
        :rtype: bytes
        """
        return b"".join(
            [bytes([self.version]), multicodec.add_prefix(self.codec, self.multihash)]
        )

    def encode(self, encoding="base58btc"):
        """
        Encoded version of the raw representation

        :param str encoding: the encoding to use to encode the raw representation, should be supported by
            ``py-multibase``
        :return: encoded raw representation with the given encoding
        :rtype: bytes
        """
        return multibase.encode(encoding, self.buffer)
