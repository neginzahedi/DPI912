#!/usr/bin/python3

# ============================================================================
#   Assignment:  Milestone 1
#
#  Author:  Fatemeh Zahedi
#  Language:  Python3
#  To Compile:  -
#
#  Class:  Python for Programmers: Sockets and Security - DPI912NSA
#  Professor:  Harvey Kaduri
#  Due Date:  May 25, 2023
#  Re-Submitted:  May 30, 2023
#
# -----------------------------------------------------------------------------
#
#  Description: This script is a client which connects to the server using IPv6 and requests lottery tickets with specific type and quantity. The generated tickets are displayed on the console and saved to GeneratedTickets.txt file.
#
#
#  Collaboration:  -
#
#  Input: The user can provide the following command-line arguments:
#         -H/--host: Server IPv6 address (default is ::1)
#         -p/--port: Port number (default is 8888)
#         -t/--ticket: Ticket type (default is max)
#         -q/--quantity: Number of tickets (default is 1)
#         -i/--identifier: Unique identifier
#
#  Output:  Generated lottery tickets will be displayed on the console and saved to a file named "GeneratedTickets.txt" in the current directory. Each ticket is preceded by the unique identifier (if provided).
#
#  Algorithm:
#    1. Parse the command-line arguments provided by the user.
#    2. Create a socket with IPv6 address family.
#    3. Connect to the server using the specified host and port.
#    4. Send a request to the server for generating lottery tickets of the specified type and quantity.
#    5. Receive the response from the server.
#    6. Print the response on the console.
#    7. If an identifier is provided, write the identifier and the response to the "GeneratedTickets.txt" file.
#    8. Close the client socket.
#
#  Required Features Not Included:  -
#
#  Known Bugs:  -
#
#  Classification: -
#
# ============================================================================

import argparse
import socket
import os

def requestTickets(host, port, ticketType, quantity, identifier):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        clientSocket.connect((host, port))
        print(f"Connected to {host}:{port}")

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

def main():
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator (Client)")
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1", help="Server IPv4 address (default is 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int, default=8888, help="Port number (default is 8888)")
    parser.add_argument("-t", "--ticket", type=str, default="max", help="Ticket type (default is max)")
    parser.add_argument("-q", "--quantity", type=int, default=1, help="Number of tickets (default is 1)")
    parser.add_argument("-i", "--identifier", type=str, default="none", help="Unique identifier")
    args = parser.parse_args()
    requestTickets(args.host, args.port, args.ticket, args.quantity, args.identifier)

if __name__ == "__main__":
    main()
