import torch
import zlib
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Load GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Ensure model is in evaluation mode
model.eval()


# Function to get next token IDs
def get_next_token_ids(current_tokens, top_k=8):
    inputs = torch.tensor([current_tokens])
    with torch.no_grad():
        outputs = model(inputs)
        # Get logits for the last token
        logits = outputs.logits[0, -1, :]
        # Apply softmax to get probabilities
        probs = torch.softmax(logits, dim=-1)
    # Get the top K token IDs
    top_probs, top_indices = torch.topk(probs, k=top_k)
    top_token_ids = top_indices.tolist()
    return top_token_ids


# Hamming(7,4) Error Correction Code Implementation
def hamming_encode(data_bits):
    # Split data bits into chunks of 4 bits
    chunks = [data_bits[i : i + 4] for i in range(0, len(data_bits), 4)]
    encoded_bits = ""
    for chunk in chunks:
        while len(chunk) < 4:
            chunk += "0"  # Pad with zeros if necessary
        d = [int(b) for b in chunk]
        # Calculate parity bits
        p1 = d[0] ^ d[1] ^ d[3]
        p2 = d[0] ^ d[2] ^ d[3]
        p3 = d[1] ^ d[2] ^ d[3]
        # Arrange bits in the order: p1, p2, d0, p3, d1, d2, d3
        encoded_chunk = f"{p1}{p2}{d[0]}{p3}{d[1]}{d[2]}{d[3]}"
        encoded_bits += encoded_chunk
    return encoded_bits


def hamming_decode(encoded_bits):
    # Split encoded bits into chunks of 7 bits
    chunks = [encoded_bits[i : i + 7] for i in range(0, len(encoded_bits), 7)]
    data_bits = ""
    for chunk in chunks:
        if len(chunk) < 7:
            continue  # Discard incomplete chunks
        bits = [int(b) for b in chunk]
        # Calculate syndrome bits
        s1 = bits[0] ^ bits[2] ^ bits[4] ^ bits[6]
        s2 = bits[1] ^ bits[2] ^ bits[5] ^ bits[6]
        s3 = bits[3] ^ bits[4] ^ bits[5] ^ bits[6]
        error_position = s1 * 1 + s2 * 2 + s3 * 4
        # Correct single-bit error if detected
        if error_position != 0:
            error_position -= 1  # Adjust for zero-based index
            bits[error_position] ^= 1
        # Extract data bits: bits at positions 2,4,5,6
        data_chunk = f"{bits[2]}{bits[4]}{bits[5]}{bits[6]}"
        data_bits += data_chunk
    return data_bits


# Encoding Function
def encode_message(message, bits_per_choice=3, prompt="Once upon a time"):
    # Compress the message using zlib
    compressed_message = zlib.compress(message.encode("utf-8"))
    # Convert compressed message to bits
    bit_string = "".join(format(byte, "08b") for byte in compressed_message)
    # Apply Hamming error correction encoding
    bit_string = hamming_encode(bit_string)
    # Group bits according to bits_per_choice
    bit_groups = [
        bit_string[i : i + bits_per_choice]
        for i in range(0, len(bit_string), bits_per_choice)
    ]
    # Start with the token IDs of the prompt
    current_tokens = tokenizer.encode(prompt)
    output_tokens = current_tokens.copy()
    for bits in bit_groups:
        n = int(bits, 2)  # Convert bits to integer
        # Get next token IDs
        next_token_ids = get_next_token_ids(current_tokens, top_k=2**bits_per_choice)
        # If there are not enough options, adjust n
        if n >= len(next_token_ids):
            n = len(next_token_ids) - 1
        chosen_token_id = next_token_ids[n]
        # Append chosen token ID to the output tokens
        output_tokens.append(chosen_token_id)
        # Update current tokens
        current_tokens.append(chosen_token_id)
    # Decode the output tokens to get the encoded text
    encoded_text = tokenizer.decode(output_tokens)
    return encoded_text


# Decoding Function
def decode_message(encoded_text, bits_per_choice=3, prompt="Once upon a time"):
    # Encode the encoded_text to get token IDs
    encoded_tokens = tokenizer.encode(encoded_text)
    # Get the token IDs of the prompt
    prompt_tokens = tokenizer.encode(prompt)
    # Ensure that the start of the encoded_tokens matches the prompt_tokens
    if encoded_tokens[: len(prompt_tokens)] != prompt_tokens:
        raise ValueError("Prompt does not match.")
    # The tokens after the prompt_tokens are the ones we need to decode
    tokens_to_decode = encoded_tokens[len(prompt_tokens) :]
    # Initialize current_tokens with prompt_tokens
    current_tokens = prompt_tokens.copy()
    bit_string = ""
    for token_id in tokens_to_decode:
        # Get next token IDs
        next_token_ids = get_next_token_ids(current_tokens, top_k=2**bits_per_choice)
        # Find the index of token_id in next_token_ids
        try:
            n = next_token_ids.index(token_id)
        except ValueError:
            # If the token_id is not found, assume zeros
            n = 0
        # Convert index to bits
        bits = format(n, f"0{bits_per_choice}b")
        bit_string += bits
        # Append token_id to current_tokens
        current_tokens.append(token_id)
    # Apply Hamming error correction decoding
    corrected_bit_string = hamming_decode(bit_string)
    # Convert bits back to bytes
    byte_array = []
    for i in range(0, len(corrected_bit_string), 8):
        byte = corrected_bit_string[i : i + 8]
        if len(byte) < 8:
            continue  # Discard incomplete bytes
        byte_array.append(int(byte, 2))
    # Convert byte array to bytes
    compressed_message = bytes(byte_array)
    try:
        # Decompress the message
        message = zlib.decompress(compressed_message).decode("utf-8")
    except zlib.error:
        message = ""
    return message


# Main Execution
if __name__ == "__main__":
    # Secret message to hide
    secret_message = "Hello 😊"
    # Encode the message
    encoded_text = encode_message(secret_message)
    print("Encoded Text:")
    print(encoded_text)
    # Decode the message
    decoded_message = decode_message(encoded_text)
    print("\nDecoded Message:")
    print(decoded_message)
