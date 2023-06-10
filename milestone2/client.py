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
#   Re-Submitted:  June 10, 2023
#
# -----------------------------------------------------------------------------
#
#   Description: This script is for a server to generate lottery tickets (Max, 6/49, and Daily Grand) upon client requests.
#                The server listens for incoming connections and generates random tickets based on the requested type and quantity.
#
#   Collaboration:  -
#
#   Input: python3 client.py -H <server_host> -p <server_port> -t <ticket_type> -q <quantity> -i <identifier> -n <requests>
#
#   Output: If the client successfully connects to the server and receives a response, the response will be printed to the console. 
#           The response contains the generated lottery tickets or error message if there was an issue.
#           
#
#   Algorithm: The script establishes a connection with the server and sends requests in parallel using child processes. 
#              Upon receiving responses, it prints them to the console. The responses are also appended to a file. 
#  
#   Required Features Not Included:  -
#   Known Bugs:  -
#   Classification: -
# ==============================================================================


import argparse
import os
import socket
import random

def requestTickets(host, port, ticketType, quantity, identifier):
    clientSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    try:
        clientSocket.connect((host, port))

        request = f"{ticketType},{quantity}"
        clientSocket.send(request.encode())

        response = clientSocket.recv(1024).decode()
        print(response)

        if identifier:
            with open("GeneratedTickets.txt", "a") as file:
                if not os.path.isfile("GeneratedTickets.txt"):
                    file.write("Generated Tickets:\n")
                file.write(f"Identifier: {identifier}\n")
                file.write(f"Ticket Type: {ticketType}\n")
                file.write(response)
                file.write("\n")

    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running.")

    finally:
        clientSocket.close()

def generateRequests(host, port, ticketType, quantity, identifier, requests):
    for i in range(requests):
        pid = os.fork()

        if pid == 0:
            # Child process
            requestTickets(host, port, ticketType, quantity, f"{identifier}_{i+1}")
            os._exit(os.EX_OK)  # Terminate child process
            

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Client)")
    parser.add_argument("-H", "--host", type=str, default="::1", help="Server IPv6 address (default is ::1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("-t", "--ticket", type=str, help="Ticket type (default is max)")
    parser.add_argument("-q", "--quantity", type=int, default=random.randint(1,10), help="Number of tickets per request (default is 1)")
    parser.add_argument("-i", "--identifier", type=str, default="none", help="Unique identifier")
    parser.add_argument("-n", "--requests", type=int, default=1, help="Number of requests (default is 1)")
    args = parser.parse_args()

    # Validate the provided arguments
    if not args.host or not args.port or not args.ticket or not args.quantity or not args.identifier or not args.requests:
        parser.print_help()
        return
    
    generateRequests(args.host, args.port, args.ticket, args.quantity, args.identifier, args.requests)

if __name__ == "__main__":
    main()