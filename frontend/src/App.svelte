<script lang="ts">
	import { prompts } from "./lib/prompts.json";

	let encodePrompt = "";
	let hiddenMessage = "";
	let encodedResponse = "";
	let encodeLoading = false;

	let decodePrompt = "";
	let coverMessage = "";
	let decodedResponse = "";
	let decodeLoading = false;

	$: isEncodeFormValid = () => encodePrompt && hiddenMessage && !encodeLoading;
	$: isDecodeFormValid = () => decodePrompt && coverMessage && !decodeLoading;

	// Reset encode form
	const resetEncodeForm = () => {
		encodePrompt = "";
		hiddenMessage = "";
		encodedResponse = "";
	};

	// Reset decode form
	const resetDecodeForm = () => {
		decodePrompt = "";
		coverMessage = "";
		decodedResponse = "";
	};

	const copyToClipboard = (text: string) => {
		navigator.clipboard.writeText(text);
		alert("Copied to clipboard");
	};

	const getRandomPrompt = () => {
		const randomIndex = Math.floor(Math.random() * prompts.length);
		return prompts[randomIndex];
	};

	const setRandomPrompt = (type: "encode" | "decode") => {
		const randomPrompt = getRandomPrompt();
		if (type === "encode") {
			encodePrompt = randomPrompt;
		} else {
			decodePrompt = randomPrompt;
		}
	};

	const encodeMessage = async () => {
		encodeLoading = true;
		const response = await fetch("/encode", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: encodePrompt,
				message: hiddenMessage,
			}),
		}).finally(() => {
			encodeLoading = false;
		});

		const result = await response.json();
		encodedResponse = result.encoded_message || "Error: No response from server";
	};

	const decodeMessage = async () => {
		decodeLoading = true;
		const response = await fetch("/decode", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: decodePrompt,
				cover_text: coverMessage,
			}),
		}).finally(() => {
			decodeLoading = false;
		});

		const result = await response.json();
		decodedResponse = result.decoded_message || "Error: No response from server";
	};
</script>

<svelte:head>
	<title>LLM Steganography</title>
</svelte:head>

<h1>Steganography App</h1>

<div class="form-section">
	<h2>Encode</h2>
	<form on:submit|preventDefault={encodeMessage}>
		<div class="textarea-container">
			<label for="encodePrompt">Prompt:</label>
			<textarea id="encodePrompt" bind:value={encodePrompt} placeholder="Enter prompt text"></textarea>
			<div class="floating-buttons">
				<button on:click|preventDefault={() => copyToClipboard(encodePrompt)} title="Copy" class:hide={encodePrompt === ""}>
					📋
				</button>
				<button on:click|preventDefault={resetEncodeForm} title="Reset" class:hide={encodePrompt === ""}>🔄</button>
				<button on:click|preventDefault={() => setRandomPrompt("encode")} title="Random Prompt">🎲</button>
			</div>
		</div>

		<div class="textarea-container">
			<label for="hiddenMessage">Hidden Message:</label>
			<textarea id="hiddenMessage" bind:value={hiddenMessage} placeholder="Enter hidden message"></textarea>
			<div class="floating-buttons" class:hide={hiddenMessage === ""}>
				<button on:click|preventDefault={() => copyToClipboard(hiddenMessage)} title="Copy">📋</button>
				<button on:click|preventDefault={() => (hiddenMessage = "")} title="Reset">🔄</button>
			</div>
		</div>

		<button type="submit" disabled={!isEncodeFormValid()}>
			{#if encodeLoading}
				<div class="spinner"></div>
			{:else}
				Encode
			{/if}
		</button>
	</form>

	<div class="response">
		<h3>Encoded Response:</h3>
		<p>{encodedResponse}</p>
		<div class="floating-buttons">
			<button on:click|preventDefault={() => copyToClipboard(encodedResponse)} title="Copy" class:hide={encodedResponse === ""}
				>📋</button
			>
		</div>
	</div>
</div>

<div class="form-section">
	<h2>Decode</h2>
	<form on:submit|preventDefault={decodeMessage}>
		<div class="textarea-container">
			<label for="decodePrompt">Prompt:</label>
			<textarea id="decodePrompt" bind:value={decodePrompt} placeholder="Enter prompt text"></textarea>
			<div class="floating-buttons">
				<button on:click|preventDefault={() => copyToClipboard(decodePrompt)} title="Copy" class:hide={decodePrompt === ""}
					>📋</button
				>
				<button on:click|preventDefault={() => (decodePrompt = "")} title="Reset" class:hide={decodePrompt === ""}>🔄</button>
				<button on:click|preventDefault={() => setRandomPrompt("decode")} title="Random Prompt">🎲</button>
			</div>
		</div>

		<div class="textarea-container">
			<label for="coverMessage">Cover Message:</label>
			<textarea id="coverMessage" bind:value={coverMessage} placeholder="Enter cover message"></textarea>
			<div class="floating-buttons" class:hide={coverMessage === ""}>
				<button on:click|preventDefault={() => copyToClipboard(coverMessage)} title="Copy">📋</button>
				<button on:click|preventDefault={() => (coverMessage = "")} title="Reset">🔄</button>
			</div>
		</div>

		<button type="submit" disabled={!isDecodeFormValid()}>
			{#if decodeLoading}
				<div class="spinner"></div>
			{:else}
				Decode
			{/if}
		</button>
	</form>

	<div class="response">
		<h3>Decoded Response:</h3>
		<p>{decodedResponse}</p>
		<div class="floating-buttons" class:hide={decodedResponse === ""}>
			<button on:click|preventDefault={() => copyToClipboard(decodedResponse)} title="Copy">📋</button>
		</div>
	</div>
</div>

<style>
	form {
		margin-bottom: 2rem;
		display: flex;
		flex-direction: column;
		width: 100%;
	}

	label {
		margin-bottom: 0.5rem;
		font-weight: bold;
	}

	textarea {
		resize: vertical;
		width: 100%;
		min-height: 100px;
		padding: 0.75rem;
		border: 1px solid #ccc;
		border-radius: 8px;
		font-size: 1rem;
		line-height: 1.5;
	}
	.textarea-container {
		position: relative;
		margin-bottom: 1.5rem;
		width: 100%;
	}

	.floating-buttons {
		position: absolute;
		bottom: 10px;
		right: -10px;
		display: flex;
		gap: 8px;
		opacity: 0.5;
		transition: opacity 0.3s ease;
		background-color: #1a1a1a;
		border-radius: 10px;
		overflow: hidden;
	}

	.floating-buttons button {
		background: none;
		color: white;
		border: none;
		border-radius: 50%;
		padding: 0.5rem;
		cursor: pointer;
		transition: background-color 0.3s ease;
		border-radius: 0px;
	}
	.floating-buttons button:hover {
		background-color: #474747;
	}

	.textarea-container:hover .floating-buttons {
		opacity: 1;
	}

	.hide {
		display: none;
	}

	.textarea-container {
		position: relative;
	}

	form > button {
		padding: 0.75rem 1.5rem;
		border: none;
		background-color: #007bff;
		color: white;
		font-size: 1rem;
		border-radius: 8px;
		cursor: pointer;
		transition: background-color 0.3s ease;
		width: 100%;
		margin-bottom: 1rem;
	}

	form > button:disabled {
		background-color: #ccc;
		cursor: not-allowed;
		opacity: 0.7;
	}

	.spinner {
		border: 4px solid #f3f3f3;
		border-top: 4px solid #3498db;
		border-radius: 50%;
		width: 20px;
		height: 20px;
		animation: spin 1s linear infinite;
		display: inline-block;
		vertical-align: middle;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.response {
		margin-top: 1rem;
		padding: 1rem;
		border-radius: 8px;
		border: 1px solid #ccc;
		position: relative;
	}

	.response h3 {
		margin-bottom: 0.5rem;
	}

	.response p {
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	h1,
	h2 {
		margin-bottom: 1rem;
		font-family: "Arial", sans-serif;
	}

	.form-section {
		margin-bottom: 3rem;
	}
</style>
