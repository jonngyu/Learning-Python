# Initializing the blockchain list
blockchain = []


def get_last_blockchain_value():
    """ Returns the last value of the current block. """
    return blockchain[-1]


def add_value(transaction_amount, last_transaction=[1]):
    """ Append a new value as well as the last block value to the blockchain 

    Arguments:
        :transaction_amount: The amount should be added.
        :last_transaction: The last block amount (default [1]).   
    """
    blockchain.append([last_transaction, transaction_amount])


def get_user_input():
    """ Returns the input of the user (a new transaction amount) as a float. """
    return float(input('Your transaction amount please: '))


# Get the first transaction and add the value to the blockchain
tx_amount = get_user_input()
add_value(tx_amount)

while True:
    tx_amount = get_user_input()
    add_value(tx_amount, get_last_blockchain_value())

    # Output the current blockchain list
    for block in blockchain:
        print ('Outputting Block')
        print (block)

print ('Done!')