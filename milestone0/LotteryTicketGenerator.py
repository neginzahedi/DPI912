#!/usr/bin/python3

"""
==============================================================================
   Assignment:  Milestone 0

  Author:  Fatemeh Zahedi
  Language:  Python3 (argparse, random library)
  To Compile:  n/a

  Class:  Python for Programmers: Sockets and Security - DPI912NSA
  Professor:  Harvey Kaduri
  Due Date:  May 17, 2023
  Re-Submitted:  May 25, 2023

-----------------------------------------------------------------------------

  Description:  This script allows users to generate lottery tickets of different types (Max, 6/49, and Daily Grand).

  Collaboration:  -

  Input: ./LotteryTicketGenerator.py -t <ticket> -q <quantity>
          -t, --ticket   : The type of lottery ticket to generate.
          -q, --quantity      : The number of tickets to generate.

  Output:  The user passes the ticket type and number of tickets, and the script generates random tickets, shows the numbers for each ticket and save them to "Generated Tickets.txt" file.
              *** LOTTO 6/49 Ticket(s) ***
              1. [13 32 44 45 46 47]

  Algorithm:  The LotteryTicketGenerator class stores information about different ticket types, such as their names, number ranges, and numbers per ticket.
              The generateTickets method of the class takes the ticket type and quantity as inputs and generates random tickets based on the specified type.

  Required Features Not Included:  -

  Known Bugs:  -

  Classification: -

==============================================================================
"""

import argparse
import random

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
        # store generated tickets
        tickets = []
        for _ in range(quantityOfTicket):
            # store generated ticket
            ticket = []
            # for how many numbers per ticket
            for length in typeOfTicket.numbersPerTicket:
                # store numbers within a set
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

def main():
    # create the parser
    parser = argparse.ArgumentParser(description="Lottery Ticket Generator")

    # add arguments
    parser.add_argument("-t", "--ticket", type=str, choices=["max", "6/49", "daily"],
                        help="Lottery Ticket types: LOTTO MAX (max), LOTTO 6/49 (6/49), DAILY GRAND (daily)")
    parser.add_argument("-q", "--quantity", type=int, default=1,
                        help="Number of tickets (default is 1 ticket)")
    
    # parse the arguments
    args = parser.parse_args()

    # if argument value not provided, display help message and return
    if args.ticket is None:
        parser.print_help()
        return

    # create instance of the LotteryTicketGenerator class
    generator = LotteryTicketGenerator()

    # access the argument values
    ticketTypeKey = args.ticket
    quantity = args.quantity

    # display generated tickets based on ticket type to the STDOUT and save to the file
    try:
        tickets = generator.generateTickets(quantity, generator.lottoTicketTypes[ticketTypeKey])

        with open("Generated Tickets.txt", 'w') as file:
            file.write(f"*** {generator.lottoTicketTypes[ticketTypeKey].ticketType} Ticket(s) ***\n")
            for i, ticket in enumerate(tickets, 1):
                file.write(f"{i}. {', '.join(map(str, ticket[0]))}\n")

        print(f"Tickets generated and saved to 'Generated Tickets.txt'")
        print(f"*** {generator.lottoTicketTypes[ticketTypeKey].ticketType} Ticket(s) ***")
        for i, ticket in enumerate(tickets, 1):
            print(f"{i}. {', '.join(map(str, ticket[0]))}")
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
