class CRCMismatchException(Exception):
    """
    Exception raised when the CRC of a received message does not match the expected CRC.
    """
    pass

class AckError(Exception):
    """
    Exception raised when an ACK response indicates an error.
    """
    pass