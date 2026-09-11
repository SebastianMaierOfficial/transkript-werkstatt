"""Synthetic smoke test with outgoing Python sockets and DNS blocked."""
from pathlib import Path
import socket
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'app'))
from local_model import block_outgoing_network
block_outgoing_network()
from server import analyze


def main():
    for address in [('127.0.0.1', 1), ('203.0.113.1', 443)]:
        with socket.socket() as sock:
            try:
                sock.connect(address)
            except OSError as error:
                assert 'gesperrt' in str(error)
            else:
                raise AssertionError('Socket guard not active')
    try:
        socket.getaddrinfo('example.invalid', 443)
    except OSError as error:
        assert 'gesperrt' in str(error)
    else:
        raise AssertionError('DNS guard not active')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.sendto(b'synthetic', ('203.0.113.1', 53))
        except OSError as error:
            assert 'gesperrt' in str(error)
        else:
            raise AssertionError('UDP guard not active')
    rules = [{'source': 'Sebastian', 'action': 'replace', 'target': 'Coach'},
             {'source': 'Petra', 'action': 'replace', 'target': 'Kundin'}]
    result = analyze('Sebastian: Petra kennt Thomas Zappelwitz in München.\nPetra: Zappelwitz arbeitet bei Siemens.', {}, mode='model', overrides=rules)
    assert result['text'] == 'Coach: Kundin kennt [Person] in [Ort].\nKundin: [Person] arbeitet bei [Unternehmen].'
    print('Offline-Selbsttest OK: Modell lokal geladen, Rollen/Personen/Orte/Organisationen erkannt; ausgehende Python-Netzwerkaufrufe gesperrt.')


if __name__ == '__main__':
    main()
