#!/usr/bin/python3

# ==============================================================================
#    Assignment:  Milestone 2

#   Author:  Fatemeh Zahedi
#   Language:  Python3
#   To Compile:  -

#   Class:  Python for Programmers: Sockets and Security - DPI912NSA
#   Professor:  Harvey Kaduri
#   Due Date:  Jun 4, 2023
#   Submitted:  Jun 3, 2023

# -----------------------------------------------------------------------------

#   Description: This script is for a server to generate lottery tickets (Max, 6/49, and Daily Grand) upon client requests.
#                The server listens for incoming connections and generates random tickets based on the requested type and quantity.

#   Collaboration:  -

#   Input: python server.py -H ::1 -p 8888 -s 10 (all has default)

#   Output: Server listening on, Accepted connection from [IPv6 address]:[port], Error: [error message]

#   Algorithm:
#     1. Start the server by creating a socket and binding it to the specified IPv6 address and port.
#     2. Accept a client connection and receive the client's request, which includes the ticket type and quantity of tickets requested.
#     3. Use the LotteryTicketGenerator to generate the requested number of tickets based on the ticket type and quantity. Each ticket is a list of sets, where each set represents the numbers on a ticket.
#     4. Process the generated tickets by converting them to a string format that can be sent back to the client.
#     5. Close the client connection and go back to listening for new connections

#   Required Features Not Included:  -

#   Known Bugs:  -

#   Classification: -

# ==============================================================================

import argparse
import random
import socket
import os
import signal

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

def runServer(host, port, pool_size):
    serverSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    serverSocket.bind((host, port))
    serverSocket.listen(pool_size)
    print(f"Server listening on [{host}]:{port}...")
    
    # Create a signal handler to handle child processes
    def signalHandler(signum, frame):
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid == 0:
                    break
                print(f"Child process {pid} terminated.")
            except OSError:
                break
    
    # Register the signal handler for SIGCHLD (child process termination)
    signal.signal(signal.SIGCHLD, signalHandler)
    
    while True:
        try:
            clientSocket, addr = serverSocket.accept()
            print(f"Accepted connection from [{addr[0]}]:{addr[1]}")
            
            # Fork a child process to handle the client request
            pid = os.fork()
            
            if pid == 0:  # Child process
                serverSocket.close()  # Close the server socket in the child process
                request = clientSocket.recv(1024).decode().strip()
                ticketType, quantity = request.split(',')
                processClientRequest(clientSocket, addr, ticketType, int(quantity))
                os._exit(0)
            else:  # Parent process
                clientSocket.close()  # Close the client socket in the parent process
        
        except socket.error as e:
            print(f"Socket error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Server)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("-s", "--pool_size", type=int, default=5, help="Number of processes in the pool (default is 5)")
    args = parser.parse_args()
    runServer(args.host, args.port, args.pool_size)

if __name__ == "__main__":
    main()
