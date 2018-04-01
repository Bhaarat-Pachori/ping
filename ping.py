import socket
import time
from time import monotonic as timer
import sys
import os
import struct
import select

# Global Constant variables
TYPE_REQ = 8
TYPE_RES = 0
CODE = 0
IP_HEADER_SIZE = 20
HEADER_SIZE = 8
PACKET_SIZE = 64
seq = 0x1

BIT_SHIFT = 8
TWO_BYTE_MASK = 0xffff


def check_sum(data_for_chksum):
    """
    This method is used to calculate the checksum.
    :param data_for_chksum:
    :return: checksum of the input
    """
    total = 0
    bit_at_i = 0
    while bit_at_i < len(data_for_chksum):
        bit_word_16 = 0
        try:
            bit_word_16 = data_for_chksum[bit_at_i] + (data_for_chksum[bit_at_i+1] << BIT_SHIFT)
        except IndexError:
            # this exception handles the checksum method if the data is of odd length
            bit_word_16 = data_for_chksum[len(data_for_chksum) - 1]
        carry = total + bit_word_16
        total = (carry & TWO_BYTE_MASK) + (carry >> BIT_SHIFT*2)
        bit_at_i += 2
    # returns the one's complement of the total.
    return ~total & TWO_BYTE_MASK


def create_packet_to_send(packet_id, size_to_send):
    """
    This method is used to create the packet that has to be
    sent over the socket to the destination.
    :param packet_id: is the process ID of this program
    :param size_to_send: size of the data to be sent to the
                         destination.
    :return: the request header
             the data to send
             the checksum
    """
    """
    Create ICMP Echo Request packet first.
    ICMP packet has following fields.
    1. type(8 bites) == 8
    2. code(8 bits) == 0
    3. Checksum(16 bits) = 0 initially then we have to calculate
       again once header and data is formed and insert it.
    4. Identifier(16 bits) = any valid number.
    5. Sequence Number(16 bits) = valid seq number
    """
    my_check = 0
    pad_bytes = []
    value_to_stuff = 0

    for i in range(size_to_send):
        if value_to_stuff > 255:
            value_to_stuff = 0
        pad_bytes.append(value_to_stuff)
        value_to_stuff += 1
    data_pack = bytes(pad_bytes)

    echo_req_pack = struct.pack('bbHHh', TYPE_REQ, CODE, my_check, packet_id, seq)
    my_checksum = check_sum(echo_req_pack + data_pack)
    return data_pack, socket.htons(my_checksum)


def create_socket():
    """
    This method is used to create the RAW socket of type
    prototype in this case icmp.
    :return: the created socket is returned.
    """
    icmp = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    return my_socket


def send_ping_echo_request(data_in_req, socket_to_use, process_id, destination_host, my_check):
    """
    This method sends the actual ECHO request to the destination. Before sending the
    request the checksum is inserted in the packet to be sent.
    :param data_in_req: data to be sent with icmp echo request.
    :param socket_to_use: socket id for communication
    :param process_id: the process id of this process
    :param destination_host: final host i.e. the destination
    :param my_check: checksum to be sent with the ECHO request.
    :return: the time when the request was sent to the destination
    """
    count = 0
    time_request = 0
    header = 0
    if count < count_out or no_options:
        header = struct.pack("bbHHh", TYPE_REQ, CODE, socket.htons(my_check), process_id, seq)
        echo_packet = header + data_in_req
        try:
            socket_to_use.sendto(echo_packet, (destination_host, 0))
            time_request = time.time()
        except socket.error:
            print('ping: cannot resolve '+'\"'+destination+'\"'+': Unknown Host')
            exit(0)
    return time_request


def receive_echo_reply(my_socket, ID, timeout, time_req, sequence):
    """
    This method is used to receive the reply for the ECHO REQUEST.
    :param my_socket: socket used for communication
    :param ID: process ID of this program when it runs
    :param timeout: time after which the we are not listening for any response
    :param time_req: time when the request was sent to the destination
    :param sequence: icmp packet sequence number
    :return: response for the request.
    """
    time_to_expire = timeout
    if sequence == 0:
        try:
            print('PING ', destination,socket.gethostbyaddr(destination)[2],': ', data_pckt_size, ' data bytes')
            print()
        except socket.error:
            print('ping: cannot resolve '+'\"'+destination+'\"'+': Unknown Host')
            exit(0)

    while True:
        # tuple to be used when we unpack the header received in reply.
        header = ()

        # store the time when the request was made.
        time_before_select = time.time()

        # this call for select wait for any of the file descriptors
        # namely read, write and exceptional handling. It is very
        # much same as Linux select call. If any of the descriptors
        # are ready before the timeLeft gets expired it receives the
        # data else get timeout.
        is_data_available = select.select([my_socket], [], [], time_to_expire)

        # calculate the time the select has spent waiting for the descriptors
        # to get ready.
        time_spent_in_select = (time.time() - time_before_select)

        # if timer has expired then print the appropriate message to the user
        if not len(is_data_available[0]):
            if int(time_spent_in_select) == timeout:
                print('Request timeout for', 'icmp_seq=',sequence)
            return None

        # store time if we have received the data
        time_if_data_is_received = time.time()
        echo_reply, echo_reply_from = my_socket.recvfrom(64)

        time_response = time.time()

        # Calculate the time that select has spent waiting for the response
        time_bw_req_res = time_response - time_req
        is_time_expired = time_to_expire - time_spent_in_select
        if len(echo_reply):
            sequence += 1
            ttl = int(echo_reply[8])
            print(data_pckt_size+HEADER_SIZE,' bytes from ',destination, 'icmp_seq=',sequence, ' ttl=',ttl,
                  'time=%.2f seconds'%time_bw_req_res)

        header = struct.unpack("bbHHh", echo_reply[IP_HEADER_SIZE:IP_HEADER_SIZE+HEADER_SIZE])
        if header[0] == TYPE_RES:
            sequence = 0
            return 'valid'

        if is_time_expired > 0:
            pass
        else:
            return None


def show_usage():
    print('Usage:')
    print('     ping.py google.com        [a normal ping request]')
    print('-c:  ping.py -c 5 google.com,  [sends 5 ECHO Request]')
    print('-s:  ping.py -s 4 google.com,  [send data of 10+8 bytes, "Minimum length is 0 byte"]')
    print('-i:  ping.py -i 3 google.com,  [sends request every 3 seconds]')
    print('-t:  ping.py -t 3 google.com,  [times out in 3 seconds] ')
    print('Press Enter to continue')
    input()

if __name__ == '__main__':
    """
    The program starts it execution from this point and
    perform pre-requisites here.
    1. Packet creation.
    2. Socket creation.
    3. Send ICMP ECHO request.
    4. Receive ICMP ECHO reply.
    5. Do above steps infinitely until stated.
    """
    i_wait = 1
    data_pckt_size = PACKET_SIZE - HEADER_SIZE
    time_out = 0
    count_out = 0
    default_time_out = 4
    no_options = False
    destination = ''
    # Need to mask the ID to two bytes as
    # packet ID is of two bytes in ICMP ECHO
    # request header.
    ID = os.getpid() & TWO_BYTE_MASK

    show_usage()

    # if-else ladder to parse the arguments given by
    # the user.
    if len(sys.argv) > 1:
        if sys.argv[1] == '-i':
            i_wait = int(sys.argv[2])
            destination = sys.argv[3]
        elif sys.argv[1] == '-s':
            data_pckt_size = int(sys.argv[2])
            destination = sys.argv[3]
        elif sys.argv[1] == '-t':
            time_out = float(sys.argv[2])
            destination = sys.argv[3]
        elif sys.argv[1] == '-c':
            if int(sys.argv[2]) == 0:
                exit(0)
            else:
                count_out = int(sys.argv[2])
            destination = sys.argv[3]
        else:
            destination = sys.argv[1]
    # if no arguments given run standard ping.
    if len(sys.argv) == 1:
            no_options = True

    if sys.argv[1] != '-c':
        count_out = True

    # Create packet to send.
    data, check = create_packet_to_send(ID, data_pckt_size)

    # Create end point of communication
    socket_to_communicate = create_socket()

    start_time_ping = time.time()
    sequence = 0

    # Start the infinite loop to ping the destination.
    # The loop gets terminated according to the user options.
    while count_out:
        # Sending ICMP ECHO request
        request_time = send_ping_echo_request(data, socket_to_communicate, ID, destination, check)

        # Receiving ICMP ECHO reply
        is_valid_response = receive_echo_reply(socket_to_communicate, ID, default_time_out, request_time, sequence)

        # Increment the sequence number
        sequence += 1

        current_time = time.time()

        # Check for time out, if given by user.
        # Terminate the program if time out has occurred
        if time_out:
            if current_time - start_time_ping > time_out:
                exit(0)
        if not is_valid_response:
            pass
        else:
            time.sleep(i_wait)
        if sys.argv[1] == '-c':
            count_out -= 1

