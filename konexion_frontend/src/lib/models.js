/** Model list helpers shared across the frontend. */

export const CLIENT_TYPE_LABELS = {
	groq: 'Groq',
	ollama: 'Ollama',
	open_router: 'Open Router'
};

/** Human-readable label for a model provider client_type. */
export function formatClientType(clientType) {
	return CLIENT_TYPE_LABELS[clientType] || clientType;
}

/** Filter models by search query (model id, owner, provider label). */
export function filterModels(models, searchQuery = '') {
	const query = searchQuery.trim().toLowerCase();
	if (!query) return models;

	return models.filter((model) => {
		const modelId = model.model_id?.toLowerCase() ?? '';
		const ownedBy = model.owned_by?.toLowerCase() ?? '';
		const clientType = model.client_type?.toLowerCase() ?? '';
		const clientLabel = formatClientType(model.client_type).toLowerCase();

		return (
			modelId.includes(query) ||
			ownedBy.includes(query) ||
			clientType.includes(query) ||
			clientLabel.includes(query)
		);
	});
}

/** Count models grouped by client_type. */
export function countModelsByClientType(models) {
	return models.reduce(
		(counts, model) => {
			const type = model.client_type;
			if (type === 'groq') counts.groq += 1;
			else if (type === 'ollama') counts.ollama += 1;
			else if (type === 'open_router') counts.openRouter += 1;
			return counts;
		},
		{ groq: 0, ollama: 0, openRouter: 0 }
	);
}
