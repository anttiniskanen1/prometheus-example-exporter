def parse_block(block, metric=[], labels={}):

    """Parse_block.

    Parse a 'block' of results (a level of a for example)
    and transform into a suitable list with labels and all

    """

    result = []

    # Give a dict of lists of labels which will be concatenated into a single
    # label per item. These could be static or based on the response data

    labels = {"app": ["example", "random_numbers"], "env": ["TEST"]}

    # .items() converts a dict to a list of key-value tuples
    for key, value in block.items():
        # At this point we have e.g. key-value pair 
        # "smalls: {'first': 3, 'second': 18}" based on the data
        for n_key, n_value in value.items():
            # And here "first: 3"
            # Append the list with the metric "prefixes", keys,
            # labels and value
            #
            # e.g. "example1", "random", "smalls", "first", labels, 5
            result.append((metric + [key] + [n_key], labels, n_value))

    return result

def parse_response(response, metric=[]):
    
    """Parse_response.

    Takes as an argument a response (from an extenal system perhaps) and a list
    of "metric prefixes" such as [<application>, <category>]

    """

    result = []

    # Create a shallow copy for modification
    response = response.copy()

    # Here we might check for existence of something in the data denoting an
    # error

    # Actually parse the response after error checking
    # and add to the result list
    result.extend(parse_block(response, metric=metric))

    return result
