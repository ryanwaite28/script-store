def genPrimes():
    def is_prime(num):
        if num <= 3:
            return True

        ref = int(num // 2)
        while ref > 1:
            num_check = num % ref
            if num_check == 0:
                return False
            ref -= 1

        return True

    prime = 1
    while True:
        yield prime
        prime += 1

        check_prime = is_prime(prime)

        if check_prime == False:
            while check_prime == False:
                print('not yet prime:', prime)
                prime += 1
                check_prime = is_prime(prime)