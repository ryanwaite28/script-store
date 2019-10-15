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