import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import tqdm

if torch.cuda.is_available():
    device = "cuda"
    print("Using CUDA for GPU acceleration")
elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = "mps"
    print("Using Apple Silicon MPS for GPU acceleration")
else:
    device = "cpu"
    print("Using CPU")

model_name = "microsoft/Phi-3.5-mini-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
).to(device)


def get_next_token(prompt):
    # Tokenize the initial prompt and move it to the appropriate device
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    with torch.no_grad():
        output = model(input_ids)
    logits = output.logits[:, -1, :]

    probabilities = torch.softmax(logits, dim=-1).squeeze()
    top_probabilities, top_indices = torch.topk(probabilities, 5)

    filtered_tokens = []
    for idx in top_indices:
        token = tokenizer.convert_ids_to_tokens(idx.item())
        # Exclude special tokens (e.g., <s>, <pad>, <eos>, etc.)
        if not token.startswith("<") and not token.endswith(">"):
            filtered_tokens.append((token, probabilities[idx].item()))

    return filtered_tokens


if __name__ == "__main__":
    initial_prompt = "The future of AI is"

    prompt = initial_prompt
    for _ in range(50):
        prompt = get_next_token(prompt)
        # print(prompt)
