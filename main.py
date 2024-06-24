
def multiply(n):
    return 2*n


def funcc(*args, **kargs):
    print(kargs)
    print(args)



simple_list = [1, 2, 3, 4]

funcc(*simple_list, name='mukul', age=29)




#
# print(list(map(multiply, simple_list)))
# print(simple_list)
