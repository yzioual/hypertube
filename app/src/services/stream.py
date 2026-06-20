import libtorrent as lt
import sys
import time

"""
lt.session = we need a session (one per application: manages all network activity, DHT,
    and peer connection).

lt.torrent_handle = A reference to one active torrent. Use it to query status, pause/resume,
    or prioritise files.A reference to one active torrent. Use it to query status, pause/resume,
    or prioritise files.

lt.torrent_info = Parsed metadata from a .torrent file. Gives you file names, sizes, and piece layout before download.

"""

ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
info = lt.torrent_info(sys.argv[1])
h = ses.add_torrent({'ti': info, 'save_path': '.'})
s = h.status()
print('starting', s.name)

while (not s.is_seeding):
    s = h.status()
    print('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
        s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
        s.num_peers, s.state), end=' ')
    alerts = ses.pop_alerts()
    for a in alerts:
        if a.category() & lt.alert.category_t.error_notification:
            print(a)
    sys.stdout.flush()
    time.sleep(1)
print(h.status().name, 'complete')
