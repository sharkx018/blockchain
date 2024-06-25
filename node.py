from blockchain import Blockchain
from utility.verfication import Verification


class Node:

    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'mukul'
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))

        return tx_recipient, tx_amount

    def get_user_choice(self):
        return input('Your choice: ')

    def print_blockchain_elements(self):
        # Output the blockchain list to the console
        for block in self.blockchain.get_chain():
            print('Outputting block')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        waiting_for_input = True

        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain block')
            print('5: Check transactions validity')
            # print('v: Verify the chain')
            print('q: Quit')

            user_choice = self.get_user_choice()

            print('-' * 10, 'Choice Registered', '-' * 10)

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Transaction added.')
                else:
                    print('Invalid transaction')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '5':

                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid.')
                else:
                    print('There are invalid transactions')
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please check the value from the list!')

            if not Verification.verify_chain(self.blockchain.get_chain()):
                self.print_blockchain_elements()
                break
            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balance()))
            # print("get_balance-->>", get_balance(owner))
        else:
            print('User Left!')

        print('Done!')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
