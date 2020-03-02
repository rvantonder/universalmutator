from __future__ import print_function

def myfunction(x):
    if (x < 6):
        print(x,
              y,
              z)
        x = 20
    while (x > 10):
        x -= 1
    return x

def main():
    y = 4
    v = myfunction(y)
    # v = myfunction(y) # A Python comment won't get mutated
    v = "v = myfunction(y)" # A Python string won't get mutated
    assert v==10

if __name__ == '__main__':
    main()
