def hamming_encode(bit_string):
    encoded_bits = ""
    for i in range(0, len(bit_string), 4):
        data_bits = bit_string[i : i + 4]
        if len(data_bits) < 4:
            data_bits = data_bits.ljust(4, "0")  # Pad with zeros if necessary
        d = [int(b) for b in data_bits]
        p1 = (d[0] + d[1] + d[3]) % 2
        p2 = (d[0] + d[2] + d[3]) % 2
        p3 = (d[1] + d[2] + d[3]) % 2
        encoded_word = f"{p1}{p2}{d[0]}{p3}{d[1]}{d[2]}{d[3]}"
        encoded_bits += encoded_word
    return encoded_bits


def hamming_decode(bit_string):
    decoded_bits = ""
    for i in range(0, len(bit_string), 7):
        code_bits = bit_string[i : i + 7]
        if len(code_bits) < 7:
            continue  # Discard incomplete code words
        c = [int(b) for b in code_bits]
        # Parity checks
        p1 = (c[0] + c[2] + c[4] + c[6]) % 2
        p2 = (c[1] + c[2] + c[5] + c[6]) % 2
        p3 = (c[3] + c[4] + c[5] + c[6]) % 2
        error_position = p1 * 1 + p2 * 2 + p3 * 4
        if error_position != 0:
            # Correct the error
            c[error_position - 1] ^= 1
        # Extract data bits
        data_bits = f"{c[2]}{c[4]}{c[5]}{c[6]}"
        decoded_bits += data_bits
    return decoded_bits
