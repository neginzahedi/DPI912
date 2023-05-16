import argparse
import random

class LotteryTicketGenerator:
    def __init__(self):
        self.lotto_ticket_types = {
            'max': {'name': 'LOTTO MAX', 'numbers_range': list(range(1, 50)), 'numbers_per_ticket': 7},
            '649': {'name': 'LOTTO 6/49', 'numbers_range': list(range(1, 49)), 'numbers_per_ticket': 6},
            'daily': {'name': 'DAILY GRAND', 'numbers_range': list(range(1, 49)), 'numbers_per_ticket': 5}
        }

    def tickets_generator(self, key, quantity):
        if key not in self.lotto_ticket_types:
            raise ValueError(f"Invalid ticket type '{key}'")

        ticket = self.lotto_ticket_types[key]
        numbers_range = ticket['numbers_range']
        numbers_per_ticket = ticket['numbers_per_ticket']

        tickets = []
        for _ in range(quantity):
            ticket = random.sample(numbers_range, numbers_per_ticket)
            ticket.sort()
            tickets.append(ticket)

        return tickets

def main():
    # create the parser
    parser = argparse.ArgumentParser(description='Lottery Ticket Generator')

    # add arguments
    parser.add_argument('-t', '--ticket_type', type=str, choices=['max', '649', 'daily'],
                        help='Lottery Ticket types: max (Lotto Max), 649 (Lotto 649), daily (Daily Grand)')
    parser.add_argument('-q', '--quantity', type=int, default=1,
                        help='Number of tickets to generate (default is 1 ticket)')
    
    # parse the arguments
    args = parser.parse_args()

    # if argument value not provided display help message and return
    if args.ticket_type is None:
        parser.print_help()
        return

    # create instance of the LotteryTicketGenerator class
    generator = LotteryTicketGenerator()

    # access the argument values
    ticket_type_key = args.ticket_type
    quantity = args.quantity

    # display generated tickets based on ticket type
    try:
        tickets = generator.tickets_generator(ticket_type_key, quantity)
        print(f"*** {generator.lotto_ticket_types[ticket_type_key]['name']} Ticket(s) ***")
        for i, ticket in enumerate(tickets, 1):
            print(f"{i}. [{' '.join(map(str, ticket))}]")
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
