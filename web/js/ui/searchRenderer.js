// Rendering of search results list
// Usage: renderSearchResults(uiInstance, itemsArray)

const PLACEHOLDER_IMAGE_URL = `/extensions/ComfyUI-HuggingFace/images/placeholder.jpg`;

export function renderSearchResults(ui, items) {
  ui.feedback?.ensureFontAwesome();

  if (!items || items.length === 0) {
    const queryUsed = ui.searchQueryInput && ui.searchQueryInput.value.trim();
    const typeFilterUsed = ui.searchTypeSelect && ui.searchTypeSelect.value !== 'any';
    const baseModelFilterUsed = ui.searchBaseModelSelect && ui.searchBaseModelSelect.value !== 'any';
    const message = (queryUsed || typeFilterUsed || baseModelFilterUsed)
      ? 'No models found matching your criteria.'
      : 'Enter a query or select filters and click Search.';
    ui.searchResultsContainer.innerHTML = `<p>${message}</p>`;
    return;
  }

  const placeholder = PLACEHOLDER_IMAGE_URL;
  const onErrorScript = `this.onerror=null; this.src='${placeholder}'; this.style.backgroundColor='#444';`;
  const fragment = document.createDocumentFragment();

  items.forEach(hit => {
    const modelId = hit.id;
    if (!modelId) return;

    // Extract base repository ID from full path (remove /tree/main, /blob/main, etc.)
    const baseRepoId = modelId.split('/tree/')[0].split('/blob/')[0].split('/raw/')[0];

    // HuggingFace search results do not expose a `user` object like CivitAI;
    // derive the creator from the repo id (org/user part).
    const creator = (hit.user?.username || baseRepoId.split('/')[0] || 'Unknown Creator').trim();
    const modelName = hit.name || baseRepoId.split('/').pop() || 'Untitled Model';
    const modelTypeApi = hit.type || 'other';
    const stats = hit.metrics || {};
    const tags = hit.tags?.map(t => (typeof t === 'string' ? t : t.name)).filter(Boolean) || [];

    const thumbnailUrl = hit.thumbnailUrl || placeholder;
    const firstImage = Array.isArray(hit.images) && hit.images.length > 0 ? hit.images[0] : null;
    const thumbnailType = firstImage?.type;

    const publishedAt = hit.publishedAt;
    let lastUpdatedFormatted = 'N/A';
    if (publishedAt) {
      try {
        const date = new Date(publishedAt);
        lastUpdatedFormatted = date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
      } catch (_) {}
    }

    const listItem = document.createElement('div');
    listItem.className = 'huggingface-search-item';
    listItem.dataset.modelId = baseRepoId;
    listItem.dataset.repoId = baseRepoId;

    let thumbnailHtml = '';
    const videoTitle = `Video preview for ${modelName}`;
    const imageAlt = `${modelName} thumbnail`;
    if (thumbnailUrl && typeof thumbnailUrl === 'string' && thumbnailType === 'video') {
      thumbnailHtml = `
        <video class="huggingface-search-thumbnail" src="${thumbnailUrl}" autoplay loop muted playsinline
               title="${videoTitle}"
               onerror="console.error('Failed to load video preview:', this.src)">
          Your browser does not support the video tag.
        </video>
      `;
    } else {
      const effective = thumbnailUrl || placeholder;
      thumbnailHtml = `
        <img src="${effective}" alt="${imageAlt}" class="huggingface-search-thumbnail" loading="lazy" onerror="${onErrorScript}">
      `;
    }

    listItem.innerHTML = `
      <div class="huggingface-thumbnail-container">
        ${thumbnailHtml}
        <div class="huggingface-type-badge" data-type="${modelTypeApi.toLowerCase()}">${modelTypeApi}</div>
      </div>
      <div class="huggingface-search-info">
        <h4>${modelName}</h4>
        <div class="huggingface-search-meta-info">
          <span title="Creator: ${creator}"><i class="fas fa-user"></i> ${creator}</span>
          <span title="Downloads"><i class="fas fa-download"></i> ${stats.downloadCount?.toLocaleString() || 0}</span>
          <span title="Likes"><i class="fas fa-thumbs-up"></i> ${stats.thumbsUpCount?.toLocaleString() || 0}</span>
          ${lastUpdatedFormatted !== 'N/A' ? `<span title="Published"><i class="fas fa-calendar-alt"></i> ${lastUpdatedFormatted}</span>` : ''}
        </div>
        ${tags.length > 0 ? `
        <div class="huggingface-search-tags" title="${tags.join(', ')}">
          ${tags.slice(0, 6).map(tag => `<span class="huggingface-search-tag">${tag}</span>`).join('')}
          ${tags.length > 6 ? `<span class="huggingface-search-tag">...</span>` : ''}
        </div>
        ` : ''}
      </div>
      <div class="huggingface-search-actions">
        <a href="https://huggingface.co/${baseRepoId}" target="_blank" rel="noopener noreferrer"
           class="huggingface-button small" title="Open on HuggingFace website">
          View <i class="fas fa-external-link-alt"></i>
        </a>
        <button class="huggingface-button primary small huggingface-search-browse-button"
                data-repo-id="${baseRepoId}"
                title="Browse files and folders in this repository">
          Browse <i class="fas fa-folder-tree"></i>
        </button>
        <button class="huggingface-button secondary small huggingface-search-download-repo-button"
                data-repo-id="${baseRepoId}"
                title="Download the entire repository (snapshot_download)">
          Repo <i class="fas fa-box"></i>
        </button>
      </div>
    `;

    fragment.appendChild(listItem);
  });

  ui.searchResultsContainer.innerHTML = '';
  ui.searchResultsContainer.appendChild(fragment);
}
