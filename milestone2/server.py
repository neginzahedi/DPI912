#!/usr/bin/python3

# ==============================================================================
#   Assignment:  Milestone 2
#
#   Author:  Fatemeh Zahedi
#   Language:  Python3
#   To Compile:  -
#
#   Class:  Python for Programmers: Sockets and Security - DPI912NSA
#   Professor:  Harvey Kaduri
#   Due Date:  June 4, 2023
#   Re-Submitted:  June 4, 2023
#
# -----------------------------------------------------------------------------
#
#   Description: This script is for a server to generate lottery tickets (Max, 6/49, and Daily Grand) upon client requests.
#                The server listens for incoming connections and generates random tickets based on the requested type and quantity.
#
#   Collaboration:  -
#
#   Input: python server.py -H ::1 -p 8888 (default values)
#
#   Output: 
#           Server listening on [::1]:8888...
#           Accepted connection from [client_address]:client_port
#
#   Algorithm: This algorithm enables the server to handle multiple client connections concurrently 
#              and non-blockingly by forking child processes to handle each client request. 
#              The server listens for connections without blocking and uses signal handling
#              to prevent zombie processes.
#  
#   Required Features Not Included:  -
#   Known Bugs:  -
#   Classification: -
# ==============================================================================

import argparse
import random
import socket
import signal
import os
import errno

class LotteryTicket:
    def __init__(self, ticketType, numbersPerTicket, numbersRange):
        self.ticketType = ticketType
        self.numbersPerTicket = numbersPerTicket
        self.numbersRange = numbersRange

class LotteryTicketGenerator:
    def __init__(self):
        self.lottoTicketTypes = {
            "max": LotteryTicket("LOTTO MAX", [7], 50),
            "6/49": LotteryTicket("LOTTO 6/49", [6], 49),
            "daily": LotteryTicket("DAILY GRAND", [5], 49)
        }
    
    def generateTickets(self, quantityOfTicket, typeOfTicket):
        tickets = []
        for _ in range(quantityOfTicket):
            ticket = []
            for length in typeOfTicket.numbersPerTicket:
                ticketSet = []
                ticketPool = list(range(1, typeOfTicket.numbersRange))
                remainingPool = len(ticketPool) - 1 if ticketPool else None
                for _ in range(length):
                    if ticketPool:
                        randomIndex = random.randint(0, remainingPool)
                        ticketSet.append(ticketPool.pop(randomIndex))
                        remainingPool -= 1
                ticket.append(ticketSet)
            tickets.append(ticket)
        return tickets

def processClientRequest(clientSocket, addr, ticketType, quantity):
    generator = LotteryTicketGenerator()
    
    try:
        tickets = generator.generateTickets(quantity, generator.lottoTicketTypes[ticketType])
        
        processedTickets = ""
        for i, ticket in enumerate(tickets, 1):
            processedTickets += f"{i}. {', '.join(map(str, ticket[0]))}\n"
        
        clientSocket.send(processedTickets.encode())
    
    except (ValueError, KeyError) as e:
        errorMessage = f"Error: {str(e)}"
        clientSocket.send(errorMessage.encode())
    
    clientSocket.close()

def runServer(host, port):
    serverSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    serverSocket.setblocking(False)  # Set socket to non-blocking mode
    print(f"Server listening on [{host}]:{port}...")

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)  # Prevent zombies

    while True:
        try:
            try:
                clientSocket, addr = serverSocket.accept()
                print(f"Accepted connection from [{addr[0]}]:{addr[1]}")

                pid = os.fork()

                if pid == 0:
                    # Child process
                    serverSocket.close()  # Release socket in child process
                    handleClient(clientSocket, addr)
                    os._exit(os.EX_OK)  # Terminate child process

                else:
                    # Parent process
                    clientSocket.close()  # Release socket in parent process

            except socket.error as e:
                # Handle interrupted system call error
                if e.errno == errno.EINTR:
                    continue
                elif e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    # No more incoming connections, continue loop
                    continue
                else:
                    raise

        except KeyboardInterrupt:
            # Terminate the server on keyboard interrupt (Ctrl+C)
            print("Server terminated.")
            break

    serverSocket.close()

def handleClient(clientSocket, addr):
    request = clientSocket.recv(1024).decode().strip()
    ticketType, quantity = request.split(',')
    processClientRequest(clientSocket, addr, ticketType, int(quantity))
    clientSocket.close()

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Server)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    args = parser.parse_args()
    runServer(args.host, args.port)

if __name__ == "__main__":
    main()
