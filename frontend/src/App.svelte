<script lang="ts">
	let encryptPrompt = "";
	let hiddenMessage = "";
	let encryptedResponse = "";

	let decryptPrompt = "";
	let coverMessage = "";
	let decryptedResponse = "";

	// Check if the encryption form fields are filled
	$: isEncryptFormValid = () => encryptPrompt && hiddenMessage;

	// Check if the decryption form fields are filled
	$: isDecryptFormValid = () => decryptPrompt && coverMessage;

	const encryptMessage = async () => {
		const response = await fetch("/encode", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: encryptPrompt,
				message: hiddenMessage,
			}),
		});

		const result = await response.json();
		encryptedResponse = result.cover_text || "Error: No response from server";
	};

	const decryptMessage = async () => {
		const response = await fetch("/decode", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: decryptPrompt,
				cover_text: coverMessage,
			}),
		});

		const result = await response.json();
		decryptedResponse = result.secret_message || "Error: No response from server";
	};
</script>

<svelte:head>
	<title>LLm Steganography</title>
</svelte:head>

<h1>Steganography App</h1>

<!-- Encryption Section -->
<div class="form-section">
	<h2>Encryption</h2>
	<form on:submit|preventDefault={encryptMessage}>
		<div>
			<label for="encryptPrompt">Prompt:</label>
			<textarea id="encryptPrompt" bind:value={encryptPrompt} placeholder="Enter prompt text"></textarea>
		</div>

		<div>
			<label for="hiddenMessage">Hidden Message:</label>
			<textarea id="hiddenMessage" bind:value={hiddenMessage} placeholder="Enter hidden message"></textarea>
		</div>

		<button type="submit" disabled={!isEncryptFormValid()}>Encrypt</button>
	</form>

	<div class="response">
		<h3>Encrypted Response:</h3>
		<p>{encryptedResponse}</p>
	</div>
</div>

<!-- Decryption Section -->
<div class="form-section">
	<h2>Decryption</h2>
	<form on:submit|preventDefault={decryptMessage}>
		<div>
			<label for="decryptPrompt">Prompt:</label>
			<textarea id="decryptPrompt" bind:value={decryptPrompt} placeholder="Enter prompt text"></textarea>
		</div>

		<div>
			<label for="coverMessage">Cover Message:</label>
			<textarea id="coverMessage" bind:value={coverMessage} placeholder="Enter cover message"></textarea>
		</div>

		<button type="submit" disabled={!isDecryptFormValid()}>Decrypt</button>
	</form>

	<div class="response">
		<h3>Decrypted Response:</h3>
		<p>{decryptedResponse}</p>
	</div>
</div>

<style>
	form {
		margin-bottom: 2rem;
		display: flex;
		flex-direction: column;
	}

	label {
		margin-bottom: 0.5rem;
		font-weight: bold;
	}

	textarea {
		resize: vertical;
		width: 100%;
		min-height: 100px;
		margin-bottom: 1.5rem;
		padding: 0.75rem;
		border: 1px solid #ccc;
		border-radius: 8px;
		font-size: 1rem;
		line-height: 1.5;
	}

	button {
		padding: 0.75rem 1.5rem;
		border: none;
		background-color: #007bff;
		color: white;
		font-size: 1rem;
		border-radius: 8px;
		cursor: pointer;
		transition: background-color 0.3s ease;
		align-self: flex-start;
		opacity: 1;
	}

	button:disabled {
		background-color: #ccc;
		cursor: not-allowed;
		opacity: 0.7;
	}

	.response {
		margin-top: 1rem;
		padding: 1rem;
		border-radius: 8px;
		border: 1px solid #ccc;
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
