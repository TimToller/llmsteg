import torch
import zlib
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import random
import numpy as np
from error_correction import hamming_encode, hamming_decode

# Set random seeds for reproducibility
seed_value = 42
random.seed(seed_value)
np.random.seed(seed_value)
torch.manual_seed(seed_value)

# For deterministic behavior
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# Device selection
if torch.cuda.is_available():
    device = "cuda"
    print("Using CUDA for GPU acceleration")
elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = "mps"
    print("Using Apple Silicon MPS for GPU acceleration")
else:
    device = "cpu"
    print("Using CPU")

# Load model and tokenizer
model_name = "microsoft/Phi-3.5-mini-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
).to(device)
model.eval()  # Set model to evaluation mode


# Get Next Token IDs Function with Probabilities
def get_next_token_ids(token_id, past_key_values, top_k):
    input_ids = torch.tensor([[token_id]], dtype=torch.long).to(device)
    with torch.no_grad():
        outputs = model(input_ids, use_cache=True, past_key_values=past_key_values)
    logits = outputs.logits[:, -1, :]
    probabilities = torch.softmax(logits, dim=-1).squeeze()
    top_probabilities, top_indices = torch.topk(probabilities, top_k)
    return top_indices.tolist(), top_probabilities.tolist(), outputs.past_key_values


# Encoding Function with Probability Threshold and Bit String Length
def encode_message(
    message, bits_per_choice=3, prompt="The future of AI is", prob_threshold=0.9
):
    # Prepare bit string with length
    compressed_message = zlib.compress(message.encode("utf-8"))
    message_bits = "".join(format(byte, "08b") for byte in compressed_message)
    message_bits = hamming_encode(message_bits)
    bit_string_length = format(len(message_bits), "016b")  # 16 bits for length
    bit_string = bit_string_length + message_bits  # Prepend length
    bit_pointer = 0  # Keep track of the bit position
    total_bits = len(bit_string)

    # Tokenize prompt
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    past_key_values = None
    with torch.no_grad():
        outputs = model(input_ids, use_cache=True)
    past_key_values = outputs.past_key_values
    output_tokens = input_ids[0].tolist()
    current_token_id = output_tokens[-1]

    print("Encoding message:")
    with tqdm(total=total_bits, desc="Encoding Progress") as pbar:
        while bit_pointer < total_bits:
            next_token_ids, probabilities, past_key_values = get_next_token_ids(
                current_token_id, past_key_values, top_k=2**bits_per_choice
            )
            top_prob = probabilities[0]

            if top_prob >= prob_threshold:
                # Skip encoding bits, use the most probable token
                chosen_token_id = next_token_ids[0]
            else:
                # Encode bits
                bits = bit_string[bit_pointer : bit_pointer + bits_per_choice]
                if len(bits) < bits_per_choice:
                    bits = bits.ljust(
                        bits_per_choice, "0"
                    )  # Pad with zeros if necessary
                n = int(bits, 2)
                if n >= len(next_token_ids):
                    n = len(next_token_ids) - 1
                chosen_token_id = next_token_ids[n]
                bit_pointer += bits_per_choice
                pbar.update(bits_per_choice)  # Update progress bar by bits_per_choice

            output_tokens.append(chosen_token_id)
            current_token_id = chosen_token_id

        # Finish any remaining bits in the progress bar
        if bit_pointer < total_bits:
            pbar.update(total_bits - bit_pointer)

    encoded_text = tokenizer.decode(output_tokens)
    return encoded_text


# Decoding Function with Probability Threshold and Bit String Length
def decode_message(
    encoded_text, bits_per_choice=3, prompt="The future of AI is", prob_threshold=0.9
):
    encoded_tokens = tokenizer.encode(encoded_text)
    prompt_tokens = tokenizer.encode(prompt)
    if encoded_tokens[: len(prompt_tokens)] != prompt_tokens:
        raise ValueError("Prompt does not match.")
    tokens_to_decode = encoded_tokens[len(prompt_tokens) :]

    # Initialize past_key_values with the prompt
    input_ids = torch.tensor([prompt_tokens], dtype=torch.long).to(device)
    with torch.no_grad():
        outputs = model(input_ids, use_cache=True)
    past_key_values = outputs.past_key_values
    current_token_id = prompt_tokens[-1]

    bit_string = ""
    bit_string_length = None
    total_bits_expected = None
    print("Decoding message:")
    with tqdm(desc="Decoding Progress") as pbar:
        while tokens_to_decode:
            token_id = tokens_to_decode.pop(0)
            next_token_ids, probabilities, past_key_values = get_next_token_ids(
                current_token_id, past_key_values, top_k=2**bits_per_choice
            )
            top_prob = probabilities[0]

            if top_prob >= prob_threshold:
                # Skipped encoding bits at this position
                pass  # Do nothing
            else:
                # Decode bits
                try:
                    n = next_token_ids.index(token_id)
                except ValueError:
                    n = 0
                bits = format(n, f"0{bits_per_choice}b")
                bit_string += bits

                # Update progress bar
                pbar.update(bits_per_choice)

                # Check if we have read the bit string length
                if bit_string_length is None and len(bit_string) >= 16:
                    bit_string_length = int(bit_string[:16], 2)
                    total_bits_expected = bit_string_length
                    pbar.reset(total=total_bits_expected)
                    pbar.set_description("Decoding Progress")
                    pbar.update(len(bit_string) - 16)

            current_token_id = token_id

            # Stop if we have read all bits
            if (
                bit_string_length is not None
                and len(bit_string) - 16 >= bit_string_length
            ):
                bit_string = bit_string[: 16 + bit_string_length]  # Trim any extra bits
                break

        # Finish any remaining bits in the progress bar
        if bit_string_length is not None:
            bits_decoded = len(bit_string) - 16
            if bits_decoded < total_bits_expected:
                pbar.update(total_bits_expected - bits_decoded)

    if bit_string_length is None:
        print("Failed to retrieve message length.")
        return ""

    message_bits = bit_string[16 : 16 + bit_string_length]
    corrected_bit_string = hamming_decode(message_bits)
    byte_array = []
    for i in range(0, len(corrected_bit_string), 8):
        byte = corrected_bit_string[i : i + 8]
        if len(byte) < 8:
            continue  # Discard incomplete bytes
        byte_array.append(int(byte, 2))
    compressed_message = bytes(byte_array)
    try:
        message = zlib.decompress(compressed_message).decode("utf-8")
    except zlib.error:
        message = ""
    return message


# Main Execution
if __name__ == "__main__":
    # Secret message to hide
    secret_message = "I am considered a pro gamer😎"
    prompt = "The old lighthouse stood at the edge of the cliff, weathered by time, yet it held secrets no one could imagine"
    encoded_text = encode_message(secret_message, prob_threshold=0.85, prompt=prompt)
    print("\nEncoded Text:")
    print(encoded_text)
    decoded_message = decode_message(encoded_text, prob_threshold=0.85, prompt=prompt)
    print("\nDecoded Message:")
    print(decoded_message)
